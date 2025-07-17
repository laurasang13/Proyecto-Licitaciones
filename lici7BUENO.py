import os, re
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_qdrant import Qdrant
import qdrant_client
from qdrant_client.http import models as qmodels
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables import RunnableMap

# --------- 0. Variables de entorno ---------
load_dotenv()
API_KEY          = os.getenv("GOOGLE_API_KEY")
QDRANT_API_KEY   = os.getenv("QDRANT_API_KEY")
QDRANT_URL       = os.getenv("QDRANT_URL")
DOCUMENT_PATH    = "/home/reboot-student/Desktop/Licitacion/docs/Ley 9-2017 de Contratos del Sector Público.pdf"
COLLECTION_NAME  = "RAG_Licitaciones"

# --------- 1. Historial corto ---------
history = InMemoryChatMessageHistory()
def construir_historial_chat(msgs):
    partes = []
    for m in msgs[-6:]:
        partes.append(("Humano: " if isinstance(m, HumanMessage) else "Asistente: ") + m.content)
    return "\n".join(partes)

# --------- 2. LLM base ---------
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

# --------- 3. Chat casual ---------
chat_chain = (
    ChatPromptTemplate.from_messages(
        [("system","Eres un asistente de IA amistoso y útil."), ("human","{question}")]
    ) | llm
)

# --------- 4. Cargar PDF y limpiar ---------- 
loader      = PyPDFLoader(DOCUMENT_PATH)
raw_pages   = loader.load()

regex_basura = re.compile(
    r'^(Exp\.\s+XP\d+\/\d+|Página\s+\d+\/?\d*|Tel\.:|cabildo\.grancanaria\.com|'
    r'Código Seguro|Url De Verificación|^[-–.•\.\s]{5,}\d+\s*$)',
    re.IGNORECASE,
)

def filtra_basura(t: str) -> str:
    limpio = []
    for l in t.splitlines():
        l = l.strip()
        if not l:
            continue

        # 1) Cabeceras / pies
        if regex_basura.match(l):
            continue

        # 2) Índice con puntos: "7.2.- Propiedad ...... 24"
        if re.match(r'^\d+(?:\.\d+)*\.-.*\.{5,}\s*\d+\s*$', l):
            continue
        #    Índice solo puntos: ".............. 24"
        if re.match(r'^\.{5,}\s*\d+\s*$', l):
            continue

        # 3) Línea con ≥30 % puntos
        if l.count('.') / len(l) > 0.30:
            continue

        limpio.append(l)
    return "\n".join(limpio)


clean_pages = [(i, filtra_basura(p.page_content)) for i,p in enumerate(raw_pages,1) if filtra_basura(p.page_content)]

# --------- 5. Cortar por encabezados ---------
texto_total = "\n".join(t for _,t in clean_pages)
bloques     = re.split(r'\n(?=\d+(?:\.\d+)*\.-\s)', texto_total)

# – fusionar título huérfano con su párrafo –
fusionados=[]
for i,b in enumerate(bloques):
    if i==len(bloques)-1: fusionados.append(b); break
    if len(b.splitlines())==1:
        fusionados.append(b+"\n"+bloques[i+1])
    elif i>0 and len(bloques[i-1].splitlines())==1:
        continue
    else:
        fusionados.append(b)
bloques = [b.strip() for b in fusionados if b.strip()]

# --------- 6. Sub‑chunk largos + metadata ---------
splitter = RecursiveCharacterTextSplitter(chunk_size=1800, chunk_overlap=250)

def pagina_de(bloque):
    cab = bloque.splitlines()[0]
    for n,t in clean_pages:
        if cab in t:
            return n
    return "?"

chunks=[]
for bloq in bloques:
    pag = pagina_de(bloq)
    for sub in splitter.split_text(bloq):
        chunks.append(Document(page_content=f"[Página {pag}]\n{sub}", metadata={"page":pag}))

print(f"🔍  Se han generado {len(chunks)} chunks limpios")

# --------- 7. Embeddings y Qdrant ---------
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=API_KEY)

client = qdrant_client.QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
if client.collection_exists(COLLECTION_NAME):
    print("🧹  Borrando colección anterior…")
    client.delete_collection(COLLECTION_NAME)

client.create_collection(
    COLLECTION_NAME,
    vectors_config=qmodels.VectorParams(size=768, distance=qmodels.Distance.COSINE),
)

vectorstore = Qdrant(client=client, collection_name=COLLECTION_NAME, embeddings=embedding)
vectorstore.add_documents(chunks)

# --------- 8. Prompt RAG ---------
rag_prompt = PromptTemplate.from_template(
"""Actúa como un consultor experto en licitaciones públicas en España. Responde preciso y con lenguaje simple, pero no te dejes NADA atrás.
Historial:
{chat_history}

Documentación:
{context}

Pregunta: {question}"""
)
doc_chain = create_stuff_documents_chain(llm=llm, prompt=rag_prompt)

qa_chain = RunnableMap({
    "context":     lambda x: vectorstore.similarity_search(x["query"], k=10),
    "question":    lambda x: x["query"],
    "chat_history":lambda x: x["chat_history"],
}) | doc_chain

# --------- 9. Bucle principal ---------
print("🤖  Gemini RAG activo.  'salir' para terminar.\n")

while True:
    user_input = input("Tú: ")
    if user_input.lower()=="salir":
        print("🫂  ¡Hasta luego!")
        break
    try:
                # -------- 1. Recupera top‑10 vecinos --------
        raw = vectorstore.similarity_search(user_input, k=15)

        # -------- 2. Filtra bloques‑índice --------
        def es_indice(doc):
            txt = doc.page_content
            # si contiene DOS líneas con 50 puntos seguidos, fuera
            if re.search(r'\.{20,}.*\n.*\.{20,}', txt):
                return True
            # si el primer renglón acaba en un número y no hay más texto, fuera
            if re.match(r'^\[Página \d+\].*?\.{5,}\s*\d+\s*$', txt):
                return True
            return False          # deja de mirar porcentajes


        candidatos = [d for d in raw if not es_indice(d)]

        # -------- 3. Reranking léxico --------
        def peso(doc):
            palabras = set(user_input.lower().split())
            texto    = doc.page_content.lower()
            exactas  = sum(w in texto for w in palabras)
            bonus    = 2 if {'perfil','perfiles','requisitos'} & palabras else 0
            return exactas + bonus

        matches = sorted(candidatos, key=peso, reverse=True)[:10]


        if matches and any(m.page_content.strip() for m in matches):
            hist = construir_historial_chat(history.messages)

            print("\n📚  Documentos seleccionados:")
            for i,d in enumerate(matches,1):
                print(f"\n— Doc {i} —\n{d.page_content[:700]}…\nMeta:{d.metadata}")

            respuesta = qa_chain.invoke({"query":user_input,"chat_history":hist})
            print(f"\n📄  RAG: {respuesta}")
            history.add_user_message(user_input)
            history.add_ai_message(respuesta)
        else:
            resp = chat_chain.invoke({"question":user_input})
            print(f"\n🗣️  Chat: {resp.content}")
            history.add_user_message(user_input)
            history.add_ai_message(resp.content)
    except Exception as e:
        print("⚠️ ", e)