# app/models.py
from pydantic import BaseModel
from typing import Dict

#Aquí se definen los modelos de datos que se usan para validar las entradas y estructurar y documentar las salidas de la API

#PreguntasRequest es el modelo que recibe las respuestas del usuario
class PreguntasRequest(BaseModel):
    #Las respuestas se recoge en un diccionario combinado
        # - La parte de Dict[str, .....] recoge el título de la sección
        # - La parte de Dict[str, str] recoge las preguntas (clave) y sus respuestas (valor)
    respuestas: Dict[str, Dict[str, str]]

#SeccionesResponse es el modelo que devuelve el pliego técnico generado
class SeccionesResponse(BaseModel):
    objeto: str #Objeto del contrato
    indice: list[str] #índice del pliego
    secciones: Dict[str, str] #Secciones del pliego con su contenido
