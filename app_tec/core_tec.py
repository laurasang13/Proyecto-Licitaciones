# app/core.py
from .utils import inicializar_gemini
from .prompts import generar_prompt_por_seccion


#Es como si fuese el generador del pliego, ya que:
    # - Recibe respuestas
    # - Crea los prompts para cada sección y genera el contenido
    # - Devuelve un pliego téncico estrucutrado y rellenado
def procesar_pliego(respuestas: dict) -> dict:
    #Cargamos la clave del modelo Gemini
    modelo = inicializar_gemini()
    secciones_redactadas = {}
     
    #Itera por cada sección y genera el contenido del pliego
    for titulo, contenido in respuestas.items():
        prompt = generar_prompt_por_seccion(titulo, contenido) #Crea el prompt para la sección con su respuesta
        respuesta = modelo.generate_content(prompt) #Llama al modelo Gemini para generar el contenido de la sección
        secciones_redactadas[titulo] = respuesta.text #Guarda el contenido generado

    #Para añadir el objeto del contrato y usarlo para el título del pliego
    objeto_pregunta = "¿Cuál es el objeto principal del contrato? (por ejemplo: escaneo de documentos, desarrollo de software, suministro de material…)"
    objeto = respuestas.get(" Objeto del Contrato", {}).get(objeto_pregunta, "").capitalize()

    #Genera el índice del pliego
    indice = [titulo.split(". ", 1)[-1].capitalize() for titulo in secciones_redactadas]

    #Devuelve un diccionario con los resultados
    return {
        "objeto": objeto,
        "indice": indice,
        "secciones": secciones_redactadas
    }

