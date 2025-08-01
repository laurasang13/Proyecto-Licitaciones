# app/api.py
from fastapi import APIRouter
from .model_tec import PreguntasRequest, SeccionesResponse
from .core_tec import procesar_pliego
from .utils import obtener_preguntas
from fastapi.responses import PlainTextResponse

#Creamos la instancia del router
router = APIRouter()

@router.get("/preguntas")
def listar_preguntas():
    preguntas = obtener_preguntas()
    return preguntas

#Definimos un endpoint para generar el pliego técnico
@router.post("/generar", response_model=SeccionesResponse)
def generar_pliego(request: PreguntasRequest):
    resultado = procesar_pliego(request.respuestas) #Se extraen las respuestas del usuario, se pasa a procesar_pliego y devuelve respuesta JSON
    return resultado


@router.post("/generar/texto", response_class=PlainTextResponse)
def generar_pliego_texto(request: PreguntasRequest):
    resultado = procesar_pliego(request.respuestas)

    # Construir el texto plano final
    texto = f"PLIEGO TÉCNICO PARA: {resultado['objeto']}\n\n"
    texto += "ÍNDICE:\n"
    for item in resultado["indice"]:
        texto += f"- {item}\n"
    texto += "\n"

    for titulo, contenido in resultado["secciones"].items():
        texto += f"{titulo.strip().upper()}\n"
        texto += f"{contenido.strip()}\n\n"

    return texto