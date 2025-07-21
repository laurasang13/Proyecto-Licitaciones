#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, json
from pathlib import Path
from collections import defaultdict
from hashlib import sha1
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_qdrant import Qdrant
import qdrant_client
from qdrant_client.http import models as qmodels
from langchain.chains import LLMChain
from langchain_core.runnables import RunnableMap

# ────────────────────────────────────────────────────────────────────────────────
# 0. Variables de entorno
# ────────────────────────────────────────────────────────────────────────────────
load_dotenv()
API_KEY        = os.getenv("GOOGLE_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL     = os.getenv("QDRANT_URL")

COLLECTION_NAME = "RAG_Licitaciones"

# ─── CAMBIO ─── directorio de PDFs (no JSON)
PDF_DIR = "/home/reboot-student/Desktop/Licitacion/docs/Leyes/"

# ────────────────────────────────────────────────────────────────────────────────
# 1. Historial
# ────────────────────────────────────────────────────────────────────────────────
history = InMemoryChatMessageHistory()
def construir_historial_chat(msgs):
    partes = []
    for m in msgs[-6:]:
        pref = "Humano: " if isinstance(m, HumanMessage) else "Asistente: "
        partes.append(pref + m.content)
    return "\n".join(partes)

# ────────────────────────────────────────────────────────────────────────────────
# 2‑3. LLM base y chat casual
# ────────────────────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)
chat_chain = (
    ChatPromptTemplate.from_messages(
        [("system", "Eres un asistente de IA amistoso y útil."),
         ("human", "{question}")]
    )
    | llm
)

# ────────────────────────────────────────────────────────────────────────────────
# 4. Carga y troceo de artículos DESDE PDF
# ────────────────────────────────────────────────────────────────────────────────
from langchain_community.document_loaders import PyPDFLoader            # ─── CAMBIO ───

# ─── CAMBIO ───: patrones y helpers para dividir PDFs en artículos
REG_TITULO_LINEA = re.compile(
    r'^\s*(?:Artículo\s+\d+[\.\)\-:]?\s+.+?|'
    r'Disposición\s+(?:adicional|transitoria|derogatoria|final)\s+\d*[A-Z]?[\.\)\-:]?.*?|'
    r'Preámbulo|Exposición\s+de\s+motivos|Anexo\s+\w+.*?)\s*$',
    re.IGNORECASE
)
REG_ARTICULO_INLINE = re.compile(
    r'\bArtículo\s+\d+[\.\)\-:]?\s+[A-ZÁÉÍÓÚÜÑ][^\n]*',
    re.IGNORECASE
)

def split_inline_articulos(texto, pagina, titulo_padre):
    mats = list(REG_ARTICULO_INLINE.finditer(texto))
    if not mats:
        return [{"titulo": titulo_padre or "(sin título)",
                 "contenido": texto.strip(), "pagina": pagina}]
    bloques = []
    for i, m in enumerate(mats):
        inicio = m.end()
        fin    = mats[i+1].start() if i+1<len(mats) else len(texto)
        titulo = titulo_padre if i==0 and titulo_padre else m.group(0).strip()
        bloques.append({"titulo": titulo,
                        "contenido": texto[inicio:fin].strip(),
                        "pagina": pagina})
    return bloques

def procesar_pdf(ruta_pdf: Path):
    loader  = PyPDFLoader(str(ruta_pdf))
    paginas = loader.load()

    bloques, bloque = [], {"titulo": None, "contenido": "", "pagina": None}

    for doc in paginas:
        pagina = doc.metadata.get("page")
        for linea in (doc.page_content or "").splitlines():
            linea = linea.strip()
            if not linea: 
                continue
            if REG_TITULO_LINEA.match(linea):
                if bloque["titulo"] and bloque["contenido"].strip():
                    bloques.extend(
                        split_inline_articulos(bloque["contenido"],
                                               bloque["pagina"],
                                               bloque["titulo"])
                    )
                bloque = {"titulo": linea, "contenido": "", "pagina": pagina}
            else:
                bloque["contenido"] += linea + "\n"

    if bloque["titulo"] and bloque["contenido"].strip():
        bloques.extend(
            split_inline_articulos(bloque["contenido"],
                                   bloque["pagina"],
                                   bloque["titulo"])
        )
    return bloques

# ─── FIN helpers PDF ───

def split_articulo_en_partes(titulo, texto, pagina, max_chars=1800):
    buffer, partes, idx = f"{titulo}\n", [], 1
    for p in texto.splitlines():
        p = p.strip()
        if not p: continue
        if len(buffer) + len(p) < max_chars:
            buffer += p + "\n"
        else:
            partes.append(
                Document(
                    page_content=f"[Página {pagina}]\n{titulo}\n(Parte {idx})\n{buffer.strip()}",
                    metadata={"titulo": titulo, "parte": idx, "page": pagina}
                )
            )
            idx, buffer = idx + 1, p + "\n"
    if buffer.strip():
        partes.append(
            Document(
                page_content=f"[Página {pagina}]\n{titulo}\n(Parte {idx})\n{buffer.strip()}",
                metadata={"titulo": titulo, "parte": idx, "page": pagina}
            )
        )
    return partes

# ─── CAMBIO ───: carga chunks directamente desde los PDF
def cargar_chunks_desde_pdfs(carpeta):
    chunks = []
    for path in Path(carpeta).glob("*.pdf"):
        for entrada in procesar_pdf(path):
            for p in split_articulo_en_partes(
                entrada["titulo"], entrada["contenido"], entrada["pagina"]
            ):
                p.metadata["source"] = path.name
                chunks.append(p)
    return chunks

def agrupar_chunks_por_titulo(chs):
    grupos = defaultdict(list)
    for d in chs:
        grupos[d.metadata["titulo"]].append(d)
    fusion = []
    for titulo, docs in grupos.items():
        docs.sort(key=lambda d: d.metadata.get("parte", 0))
        fusion.append(
            Document(
                page_content="\n".join(d.page_content for d in docs),
                metadata=docs[0].metadata,
            )
        )
    return fusion

# ─── CAMBIO ───
chunks = cargar_chunks_desde_pdfs(PDF_DIR)

# Índice auxiliar →  número de artículo  → [chunks]
idx_por_num = defaultdict(list)
pat_num = re.compile(r"\b(\d+)\b")
for c in chunks:
    if m := pat_num.search(c.metadata["titulo"]):
        idx_por_num[m.group(1)].append(c)

# ────────────────────────────────────────────────────────────────────────────────
# 7. Embeddings y Qdrant
# ────────────────────────────────────────────────────────────────────────────────
emb = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=API_KEY)
client = qdrant_client.QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
if client.collection_exists(COLLECTION_NAME):
    client.delete_collection(COLLECTION_NAME)

client.create_collection(
    COLLECTION_NAME,
    vectors_config=qmodels.VectorParams(size=768, distance=qmodels.Distance.COSINE),
)
vectorstore = Qdrant(client=client, collection_name=COLLECTION_NAME, embeddings=emb)
vectorstore.add_documents(chunks)

# ────────────────────────────────────────────────────────────────────────────────
# 8. Cadena RAG
# ────────────────────────────────────────────────────────────────────────────────
rag_prompt = PromptTemplate.from_template(
    "Eres un consultor experto en licitaciones públicas en España. "
    "Explica con lenguaje sencillo, completo y exclusivamente apoyándote en la documentación.\n\nHistorial:\n{chat_history}\n\nDocumentación:\n{context}\n\n"
    "Pregunta: {question}"
)
doc_chain = LLMChain(llm=llm, prompt=rag_prompt)
qa_chain = RunnableMap({
    "context":     lambda x: vectorstore.similarity_search(x["query"], k=25),
    "question":    lambda x: x["query"],
    "chat_history":lambda x: x["chat_history"],
}) | doc_chain

# ─── DEBUG ───
DEBUG_SHOW_CONTEXT = True
def resumen_docs(documents):
    lineas = []
    for d in documents:
        meta = d.metadata
        lineas.append(
            f"{meta.get('source','?')} | {meta.get('titulo')[:60]} "
            f"(parte {meta.get('parte','?')}, pág. {meta.get('page','?')})"
        )
    return "\n".join(lineas)

# ────────────────────────────────────────────────────────────────────────────────
# 9. Bucle principal
# ────────────────────────────────────────────────────────────────────────────────
print("🤖  Gemini RAG activo.  'salir' para terminar.\n")

while True:
    query = input("\nTú: ").strip()
    if query.lower() == "salir":
        print("🫂  ¡Hasta luego!"); break

    try:
        num_match = re.search(r"\b(\d+)\b", query)
        if num_match and num_match.group(1) in idx_por_num:
            rel = idx_por_num[num_match.group(1)]
            rel.sort(key=lambda d: d.metadata.get("parte", 0))
            matches = agrupar_chunks_por_titulo(rel)
        else:
            vecinos = vectorstore.similarity_search(query, k=15)
            matches = agrupar_chunks_por_titulo(vecinos)

        if matches:
            hist = construir_historial_chat(history.messages)
            contexto = "\n\n".join(d.page_content for d in matches)

            out = doc_chain.invoke(
                {"question": query, "chat_history": hist, "context": contexto}
            )
            answer = out["text"] if isinstance(out, dict) else out
            print("\n📄  RAG:\n" + answer + "\n")

            history.add_user_message(query)
            history.add_ai_message(answer)
        else:
            resp = chat_chain.invoke({"question": query})
            print("\n🗣️  Chat:\n" + resp.content + "\n")
            history.add_user_message(query)
            history.add_ai_message(resp.content)

    except Exception as e:
        print("⚠️ ", e)
