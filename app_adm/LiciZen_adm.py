import argparse, asyncio, json, os, re
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
import qdrant_client
from pydantic import BaseModel, Field, validator
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_qdrant import Qdrant
from langchain import PromptTemplate, LLMChain

# ──────────────────────────────────────────────────────────────────────────────
# 0 · Variables de entorno y configuración global
# ──────────────────────────────────────────────────────────────────────────────
load_dotenv()
API_KEY         = os.getenv("GOOGLE_API_KEY")
QDRANT_API_KEY  = os.getenv("QDRANT_API_KEY")
QDRANT_URL      = os.getenv("QDRANT_URL")
COLLECTION_NAME = "Prevencion_de_blanqueo_y_finanzas_sensibles"

EU_THRESHOLDS_2025 = {"services_subcentral": 221_000}
SIMPLIFIED_LIMIT   = 215_000
ABBREV_LIMIT       = 60_000

# ──────────────────────────────────────────────────────────────────────────────
# 1 · Helpers procedimentales
# ──────────────────────────────────────────────────────────────────────────────

def procedure_type(vec: float) -> str:
    if vec >= EU_THRESHOLDS_2025["services_subcentral"]:
        return "abierto_ordinario"
    if vec <= ABBREV_LIMIT:
        return "simplificado_abreviado"
    if vec <= SIMPLIFIED_LIMIT:
        return "abierto_simplificado"
    return "abierto_ordinario"

def sara(vec: float) -> bool:
    return vec >= EU_THRESHOLDS_2025["services_subcentral"]


def ask_float(msg: str) -> float:
    """Pide un número flotante admitiendo "," como separador decimal y miles."""
    while True:
        try:
            return float(input(msg + " ").replace(".", "").replace(",", "."))
        except ValueError:
            print("❗ Introduce un número válido.")


def ask_int(msg: str) -> int:
    return int(ask_float(msg))


def ask_bool(msg: str) -> bool:
    """Pregunta cerrada Sí/No, devuelve True/False."""
    while True:
        val = input(f"{msg} (S/N): ").strip().lower()
        if val in {"s", "si", "sí"}:
            return True
        if val in {"n", "no"}:
            return False
        print("❗ Responde S o N.")

# ──────────────────────────────────────────────────────────────────────────────
# 2 · Modelos de datos (Pydantic)
# ──────────────────────────────────────────────────────────────────────────────

class Documentacion(BaseModel):
    declaracion_responsable: bool
    oferta_economica: bool
    aceptacion_pliego: bool
    equipo_cumple: bool
    fecha: str

class ProteccionDatos(BaseModel):
    trata_datos: bool
    subcontrata_servidores: Optional[str] = None

class Subcontratacion(BaseModel):
    subcontratara: bool
    subcontratas_no_vinculadas: Optional[bool] = None

class CriteriosValoracion(BaseModel):
    precio_ofertado: float
    anormalmente_bajo: bool

class NextGeneration(BaseModel):
    cumple_prtr: bool
    modelos_b1b2c: Optional[bool] = None
    titular_real: Optional[str] = None

class Garantias(BaseModel):
    garantia_provisional: bool
    porcentaje_cuantia: Optional[str] = None

class Solvencia(BaseModel):
    volumen_anual_negocios_min: float
    importe_anual_similares_min: float
    seguro_rcp_min: float

class Ponderacion(BaseModel):
    metodologia_plan: float
    equipo_experiencia: float
    dnsh_sostenibilidad: float
    oferta_economica: float

class Datos(BaseModel):
    # Bloque 1: Datos del contrato
    objeto_contrato: str
    necesidad_resuelta: str
    responsable_contrato: str
    lugar_prestacion: str
    vec_justificado: Optional[str] = None
    


    # Bloque 2: Presupuesto
    pbl_sin_iva: float = Field(gt=0)
    iva: float = Field(gt=0)
    duracion_meses: int = Field(gt=0)
    prorrogas: int = Field(ge=0)

    # Cálculos automáticos
    vec: Optional[float] = None
    procedimiento: Optional[str] = None
    sara: Optional[bool] = None

    # Bloques 3‑12
    documentacion: Documentacion
    proteccion_datos: ProteccionDatos
    subcontratacion: Subcontratacion
    criterios: CriteriosValoracion
    nextgen: NextGeneration
    garantias: Garantias
    solvencia: Solvencia
    ponderacion: Ponderacion
    
    # ── Validadores automáticos ────────────────────────────────────────────

@validator("iva", pre=True)
def normalizar_iva(cls, v):
    v_normalizado = v / 100 if v > 1 else v
    iva_permitidos = [0.0, 0.04, 0.10, 0.21]
    if round(v_normalizado, 2) not in iva_permitidos:
        raise ValueError("⚠️ El IVA debe ser 0%, 4%, 10% o 21%. El valor recibido no es válido en España.")
    return v_normalizado


@validator("vec", always=True)
def calcula_vec(cls, v, values):
    pbl = values.get("pbl_sin_iva")
    dur = values.get("duracion_meses")
    pro = values.get("prorrogas")

    if v is not None:
        if pbl and v < pbl:
            raise ValueError("⚠️ El VEC no puede ser inferior al PBL sin IVA.")
        return v

    return pbl * (dur + pro) / dur if None not in (pbl, dur, pro) else None


@validator("procedimiento", always=True)
def asigna_proc(cls, v, values):
    vec = values.get("vec")
    return procedure_type(vec) if vec else None


@validator("sara", always=True)
def asigna_sara(cls, v, values):
    vec = values.get("vec")
    if vec is None:
        return None
    umbral_doue = 215000
    return vec >= umbral_doue


@validator("vec_justificado", always=True)
def justificar_vec(cls, v, values):
    vec = values.get("vec")
    pbl = values.get("pbl_sin_iva")
    if vec and pbl and vec > pbl * 1.1:
        return "El VEC incluye una estimación prudente de posibles modificaciones conforme al art. 101.12 LCSP."
    return None



# ──────────────────────────────────────────────────────────────────────────────
# 3 · LLM + Embeddings + Vectorstore
# ──────────────────────────────────────────────────────────────────────────────
llm    = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, streaming=True)
emb    = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=API_KEY)
client = qdrant_client.QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
vectorstore = Qdrant(client=client, collection_name=COLLECTION_NAME, embeddings=emb)

# ──────────────────────────────────────────────────────────────────────────────
# 4 · Secciones y prompts
# ──────────────────────────────────────────────────────────────────────────────
SECCIONES = [
    "Portada", "Objeto del contrato", "Procedimiento de adjudicación", "Condiciones de ejecución",
    "Garantías", "Solvencia y clasificación", "Criterios de adjudicación",
    "Obligaciones de confidencialidad y protección de datos", "Cláusula ambiental y DNSH", "Firma",
]
PAUTAS = {
    "Portada": "Incluye órgano de contratación, título, fecha y número de expediente.",
    "Firma":   "Inserta {fecha} y espacio para dos firmantes (nombre y cargo).",
}
PROMPT = PromptTemplate.from_template(
    "Eres jurista experto en contratación pública española.\n"
    "Redacta exclusivamente la sección «{titulo}». No incluyas ninguna otra parte del pliego ni repitas información de otras secciones. Este bloque debe ser autónomo y autocontenido. No intentes revisar el pliego completo."
    "Emplea castellano técnico y formal, citando artículos de la LCSP u otras normas aplicables.\n\n"
    "Datos del contrato (JSON):\n{datos}\n\n"
    "Pautas adicionales: {pautas}\n\n"
    "Referencias normativas resumidas:\n{contexto}\n\n"
    "---\n\n"
    "⚖️ **INSTRUCCIONES Y VALIDACIONES**\n\n"

    "Evita duplicar criterios sociales o ambientales en distintas secciones. Si un criterio ya se detalla en “Condiciones especiales de ejecución”, no lo repitas en otras secciones; usa una referencia del tipo: “Véanse las condiciones especiales de ejecución”.\n\n"
    "Evita duplicar y repetir cláusulas.Puedes conservar detalles si justificas que se repiten por ser parte de distintos anexos."
    "──────────────\n"
    "🟥 **VALIDACIONES CRÍTICAS (Legalidad / Nulidad)**\n"
    "──────────────\n"
    "1. Duración y prórrogas (Art. 29.2 LCSP):\n"
    "   - La duración total (inicial + prórrogas) no debe superar los 60 meses salvo justificación.\n"
    "   - Por defecto, la prórroga no debe exceder la mitad de la duración inicial.\n"

    "2. Garantía provisional (Art. 106 LCSP):\n"
    "   - Prohíbela salvo justificación técnica expresa (riesgo técnico, defensa, etc.).\n"
    "   - Si se exige, incluye una justificación legal específica.\n"

    "3. Clasificación empresarial (Art. 77 LCSP):\n"
    "   - No la exijas salvo que esté justificada por la continuidad o naturaleza especial del servicio.\n"

    "4. IVA no permitido:\n"
    "   - Acepta solo 0%, 4%, 10% o 21%. Si aparece otro valor, marca para revisión manual.\n"

    "5. Placeholders o texto basura:\n"
    "   - Detecta valores tipo “gfdfg”, “xxxx”, “[…]”, o similares. Marca ⚠️.\n"

    "6. Incoherencia PBL / VEC / Precio ofertado:\n"
    "   - El VEC debe ser ≥ PBL + IVA.\n"
    "   - Si el precio ofertado supera el VEC, marca un aviso.\n"
    "   - Si el VEC es superior al PBL + IVA, añade: “El VEC incluye una estimación prudente de posibles modificaciones no sustanciales conforme al art. 101.12 de la LCSP.”\n"

    "7. Umbral DOUE (Art. 20 LCSP):\n"
    "   - Si PBL > 215.000 € sin IVA, incluye la obligación de publicación en DOUE.\n"
    "   - Si no lo supera, añade nota aclaratoria.\n"

    "8. PRTR / DNSH falsamente afirmado:\n"
    "   - Si en los datos consta que no se cumplen, **no incluyas** cláusulas afirmativas sobre sostenibilidad.\n"
    "   - Sustituye por: “Este contrato no incluye medidas específicas derivadas del PRTR.”\n"

    "9. Criterios de adjudicación:\n"
    "   - La suma de los porcentajes debe ser exactamente 100%.\n"
    "   - Si no lo es, redistribuye proporcionalmente o lanza advertencia clara.\n"

    "10. Contradicciones internas:\n"
    "   - Si el texto contiene afirmaciones opuestas (ej. exige garantía y luego dice que no), elimina la inconsistente y deja nota de revisión.\n\n"

    "──────────────\n"
    "🟧 **VALIDACIONES TÉCNICAS Y DE COHERENCIA**\n"
    "──────────────\n"
    "1. Datos incompletos:\n"
    "   - Si algún documento o requisito (declaración responsable, oferta, etc.) no ha sido aportado, no asumas que sí lo está. Marca [PENDIENTE DE APORTAR].\n"

    "2. Subcontratación con empresas vinculadas:\n"
    "   - Si se indica que hay subcontratistas vinculados, incluye una cláusula de control y autorización expresa por parte del órgano de contratación.\n"

    "3. Protección de datos:\n"
    "   - Si se subcontratan servidores (Dropbox, AWS…), incluye cláusula específica sobre encargo de tratamiento.\n"

    "4. Corrección de campos vacíos:\n"
    "   - Si “lugar_prestacion” está vacío, reemplaza por el marcador [POR COMPLETAR].\n"

    "5. Estética y legibilidad:\n"
    "   - No repitas títulos innecesariamente.\n"
    "   - Usa encabezados consistentes y limpios.\n"
    "   - Si alguna sección es breve, amplíala MUCHO con estilo técnico y lenguaje de pliegos oficiales.\n"
    "   - Devuelve únicamente el texto limpio del pliego."
    "   - Si existe la posibilidad de crear tablas para ciertos puntos, hazlas."
    "   - No añadas fechas en la cabecera ni en la firma."
    "   - Añade la fecha que se ha desglosado en las preguntas."
    "   - Incluye 'Según art. 147.2 LCSP. En caso de empate, se priorizará la oferta con mayor puntuación en el criterio de sostenibilidad. Si persiste, se resolverá por sorteo público.'"
    "──────────────\n"
    "🟩 **CIERRE DEL PLIEGO**\n"
    "──────────────\n"
)

REVISION_FINAL = PromptTemplate.from_template(
    "Actúa como técnico de contratación pública experto.\n"
    "Tu tarea es hacer una **revisión final completa del pliego completo generado por secciones**:\n\n"
    "1. Elimina repeticiones y contradicciones internas.\n"
    "2. **No insertes notas o avisos ⚠️ dentro del texto del pliego.** El cuerpo debe quedar limpio y profesional.\n"
    "`## ⚠️ ADVERTENCIAS Y PUNTOS A REVISAR`\n"
    "Devuelve únicamente el texto limpio del pliego"
    "No pongas en el inicio 'pliego completo revisado'"
    "Da el expediente únicamente con todos los cambios. No hables como una IA dentro del pliego ni antes de la portada."
    "Devuelvelo como una licitacion oficial real"
    "Texto del pliego:\n{pliego}"
    
)



CADENAS: Dict[str, LLMChain] = {s: (PROMPT | llm) for s in SECCIONES}

# ──────────────────────────────────────────────────────────────────────────────
# 5 · Contexto legal selectivo
# ──────────────────────────────────────────────────────────────────────────────

def contexto_para(titulo: str, consulta: str, k: int = 5) -> str:
    keyword = titulo.split()[0].lower()
    colecciones = [
        "Prevencion_de_blanqueo_y_finanzas_sensibles",
        " Normativa General y Contratación Pública",
        "proteccion_de_datos_y_seguridad_digital",
        "sostenibilidad_recuperacion_y_fondos_europeos"
    ]

    docs = []
    for col in colecciones:
        temp_vs = Qdrant(client=client, collection_name=col, embeddings=emb)
        try:
            docs.extend(temp_vs.similarity_search(consulta, k=40))
        except Exception as e:
            print(f"⚠️ Error al buscar en '{col}': {e}")

    # Ordenamos por similitud si hay `score`, o simplemente cogemos los primeros que contengan el keyword
    candidatos = [d for d in docs if keyword in d.metadata.get("titulo", "").lower()]
    if not candidatos:
        candidatos = docs[:k]  # si no hay coincidencia por keyword, devolvemos cualquiera

    resumenes = [
        llm.invoke(f"Resume en dos líneas:\n{d.page_content}").content
        for d in candidatos[:k]
    ]
    return "\n".join(resumenes)


# ──────────────────────────────────────────────────────────────────────────────
# 6 · Redacción por sección (async)
# ──────────────────────────────────────────────────────────────────────────────
async def redactar_secciones(datos: Datos) -> Dict[str, str]:
    base_query = f"Pliego servicios informáticos — {datos.objeto_contrato}. PBL {datos.pbl_sin_iva} €, {datos.duracion_meses} meses."
    resultado: Dict[str, str] = {}

    async def tarea(sec: str):
        ctx = contexto_para(sec, base_query)
        raw = CADENAS[sec].invoke({
            "titulo": sec,
            "pautas": PAUTAS.get(sec, ""),
            "datos": json.dumps(datos.model_dump(), ensure_ascii=False, indent=2),
            "contexto": ctx,
        })
        resultado[sec] = raw.content if hasattr(raw, "content") else raw

    await asyncio.gather(*(tarea(s) for s in SECCIONES))
    return resultado

# ──────────────────────────────────────────────────────────────────────────────
# 7 · Cuestionario interactivo completo
# ──────────────────────────────────────────────────────────────────────────────

def preguntar_interactivo() -> Datos:
    print("\n📝 Rellena los datos para tu licitación:\n")

    # Bloque 1: Datos del contrato
    objeto_contrato      = input("Objeto del contrato: ")
    necesidad_resuelta   = input("Necesidad que resuelve: ")
    responsable_contrato = input("Responsable del contrato (nombre y cargo): ")
    lugar_prestacion     = input("Lugar de prestación: ")
    fecha = input("A fecha de (ej: 25 de mayo de 2024): ")

    # Bloque 2: Presupuesto
    pbl_sin_iva     = ask_float("PBL sin IVA (€):")
    iva             = ask_float("Tipo de IVA (%):")
    duracion_meses  = ask_int("Duración inicial (meses):")
    prorrogas       = ask_int("Meses de prórroga previstos:")

    # 🔍 Validación: tipo de IVA permitido
    iva_permitidos = [0, 4, 10, 21]
    while iva not in iva_permitidos:
        print("❗ IVA no permitido. Solo se aceptan 0%, 4%, 10% o 21%.")
        iva = ask_float("Introduce un tipo de IVA válido (%):")

    # 🔍 Validación: duración total máxima 60 meses
    while duracion_meses + prorrogas > 60:
        print(f"❗ Duración total del contrato ({duracion_meses + prorrogas} meses) supera el máximo legal permitido (60 meses).")
        prorrogas = ask_int("Introduce un número de meses de prórroga válido (máximo total 60 meses):")

    # 🔍 Validación: VEC ≥ PBL sin IVA
    while duracion_meses > 0 and (pbl_sin_iva * (duracion_meses + prorrogas) / duracion_meses) < pbl_sin_iva:
        print("❗ El VEC estimado no puede ser inferior al PBL sin IVA.")
        prorrogas = ask_int("Introduce un número de meses de prórroga válido para que el VEC sea coherente:")

    # Bloque 4: Documentación y requisitos
    documentacion = Documentacion(
        declaracion_responsable = ask_bool("Declaración Responsable presentada?"),
        oferta_economica        = ask_bool("Oferta económica lista?"),
        aceptacion_pliego       = ask_bool("Aceptación del pliego técnico?"),
        equipo_cumple           = ask_bool("Equipo cumple perfiles mínimos?"),
        fecha                   = fecha
    )

    # Bloque 5: Protección de datos
    trata_datos = ask_bool("¿Se tratarán datos personales por cuenta del contratante?")
    subcontrata_servidores = None
    if trata_datos:
        subcontrata_servidores = input("→ Si Sí: ¿Se subcontratarán servidores o servicios de tratamiento? Detallar: ")
    proteccion_datos = ProteccionDatos(
        trata_datos = trata_datos,
        subcontrata_servidores = subcontrata_servidores or None
    )

    # Bloque 6: Subcontratación
    subcontratara = ask_bool("¿Se subcontratará alguna parte del servicio?")
    no_vinculadas = None
    if subcontratara:
        no_vinculadas = ask_bool("→ Si Sí: ¿Las subcontratistas son empresas no vinculadas?")
    subcontratacion = Subcontratacion(
        subcontratara = subcontratara,
        subcontratas_no_vinculadas = no_vinculadas
    )

    # Bloque 7: Criterios de valoración
    criterios = CriteriosValoracion(
        precio_ofertado    = ask_float("Precio ofertado sin IVA (€):"),
        anormalmente_bajo  = ask_bool("¿Verificado que no es anormalmente bajo?")
    )

    # Bloque 8: NextGeneration / PRTR
    cumple_prtr = ask_bool("¿Cumple principios medioambientales y antifraude del PRTR?")
    modelos_b1b2c = titular_real = None
    if cumple_prtr:
        modelos_b1b2c = ask_bool("→ Si Sí: Modelos B1, B2 y C cumplimentados?")
        titular_real  = input("Titular real de la empresa: ")
    nextgen = NextGeneration(
        cumple_prtr = cumple_prtr,
        modelos_b1b2c = modelos_b1b2c,
        titular_real = titular_real
    )

    # Bloque 9: Garantías
    garantia_provisional = ask_bool("¿Exigir garantía provisional?")
    porcentaje_cuantia = None
    if garantia_provisional:
        porcentaje_cuantia = input("→ Si Sí: porcentaje o cuantía exigida: ")
    garantias = Garantias(
        garantia_provisional = garantia_provisional,
        porcentaje_cuantia = porcentaje_cuantia
    )

    # Bloque 10: Solvencia
    solvencia = Solvencia(
        volumen_anual_negocios_min    = ask_float("Volumen anual de negocios mínimo (€):"),
        importe_anual_similares_min   = ask_float("Importe anual de servicios similares mínimo (€):"),
        seguro_rcp_min                = ask_float("Seguro de responsabilidad civil profesional mínimo (€):")
    )

    # Bloque 11: Ponderación de criterios
    ponderacion = Ponderacion(
        metodologia_plan     = ask_float("% Metodología y plan de trabajo:"),
        equipo_experiencia   = ask_float("% Equipo y experiencia:"),
        dnsh_sostenibilidad  = ask_float("% DNSH / Sostenibilidad:"),
        oferta_economica     = ask_float("% Oferta económica:")
    )

    # 🔍 Validación: la suma de ponderaciones debe ser 100%
    suma_ponderacion = (
        ponderacion.metodologia_plan +
        ponderacion.equipo_experiencia +
        ponderacion.dnsh_sostenibilidad +
        ponderacion.oferta_economica
    )
    while suma_ponderacion != 100:
        print(f"❗ La suma de los porcentajes de criterios es {suma_ponderacion}%, debe ser exactamente 100%.")
        ponderacion.metodologia_plan = ask_float("% Metodología y plan de trabajo:")
        ponderacion.equipo_experiencia = ask_float("% Equipo y experiencia:")
        ponderacion.dnsh_sostenibilidad = ask_float("% DNSH / Sostenibilidad:")
        ponderacion.oferta_economica = ask_float("% Oferta económica:")
        suma_ponderacion = (
            ponderacion.metodologia_plan +
            ponderacion.equipo_experiencia +
            ponderacion.dnsh_sostenibilidad +
            ponderacion.oferta_economica
        )

    return Datos(
        objeto_contrato=objeto_contrato,
        necesidad_resuelta=necesidad_resuelta,
        responsable_contrato=responsable_contrato,
        lugar_prestacion=lugar_prestacion,
        pbl_sin_iva=pbl_sin_iva,
        iva=iva,
        duracion_meses=duracion_meses,
        prorrogas=prorrogas,
        documentacion=documentacion,
        proteccion_datos=proteccion_datos,
        subcontratacion=subcontratacion,
        criterios=criterios,
        nextgen=nextgen,
        garantias=garantias,
        solvencia=solvencia,
        ponderacion=ponderacion
        
    )

# ──────────────────────────────────────────────────────────────────────────────
# 8 · Utilidades de salida
# ──────────────────────────────────────────────────────────────────────────────

def imprimir_pliego(sec: Dict[str, str]):
    for nombre in SECCIONES:
        print(f"\n## {nombre}\n")
        print(sec[nombre].strip())

# ──────────────────────────────────────────────────────────────────────────────
# 9 · main
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera un pliego modular por secciones.")
    parser.add_argument("--json", type=Path, help="Ruta a archivo JSON con datos (opcional)")
    args = parser.parse_args()

    datos = Datos.parse_file(args.json) if args.json else preguntar_interactivo()

    print("\n⏳ Redactando secciones…\n")
    pliego = asyncio.run(redactar_secciones(datos))

    texto_pliego = "\n\n".join(f"## {sec}\n\n{contenido}" for sec, contenido in pliego.items())
    revisado = REVISION_FINAL | llm
    pliego_revisado = revisado.invoke({"pliego": texto_pliego}).content

    print(pliego_revisado)