import os
from dotenv import load_dotenv
import google.generativeai as genai

def inicializar_gemini():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")

def obtener_preguntas():
    return [
        (" Objeto del Contrato", [
            "¿Cuál es el objeto principal del contrato? (por ejemplo: escaneo de documentos, desarrollo de software, suministro de material…)",
            "¿Qué volumen estimado de trabajo incluye el contrato? (número de unidades, documentos, usuarios…)",
            "¿Cuál será la duración estimada del contrato/proyecto?",
            "¿Hay una fecha concreta de inicio prevista?"
        ]),
        (" Situación Inicial", [
            "Describe brevemente la situación actual relacionada con el objeto del contrato. ¿Qué necesita mejorar o resolverse?",
            "¿Dónde se encuentra actualmente la documentación/material que se va a tratar?",
            "¿Qué formatos y tipos de documentos/material existen? (Ej. papel A4, con tickets pegados, grapados, carpetas…)"
        ]),
        (" Servicios/Tareas a Realizar", [
            "¿Qué tareas debe realizar la empresa adjudicataria? (desglosar si hay varias)",
            "¿Qué formato de entrega final se requiere? (Ej. PDF, Word, base de datos…)",
            "¿Cómo debe organizarse la información entregada? ¿Hay alguna estructura específica que seguir?"
        ]),
        (" Fases del Proyecto", [
            "¿En cuántas fases se divide el proyecto?",
            "¿Qué tareas específicas debe realizar la empresa en cada fase?",
            "¿Cómo se verificará la finalización correcta de cada fase?"
        ]),
        (" Dirección y Supervisión de los Trabajos", [
            "¿Quién será la persona de contacto o responsable de supervisión por parte de la entidad pública?",
            "¿Con qué frecuencia se realizarán reuniones de seguimiento?"
        ]),
        (" Lugar de Realización", [
            "¿Dónde se deben realizar las tareas? ¿En dependencias del adjudicatario o de la entidad?"
        ]),
        (" Entregables y Documentación", [
            "¿Qué entregables se espera recibir por parte del adjudicatario? (Ej. disco externo, certificados, informes…)",
            "¿Qué requisitos debe cumplir la documentación entregada? (idioma, copias, soporte digital…)"
        ]),
        (" Equipo de Trabajo", [
            "¿Qué perfiles profesionales son necesarios para ejecutar el proyecto?",
            "¿Cuántas personas compondrán el equipo y cuántas horas se estima para cada uno?"
        ]),
        (" Requisitos de las Empresas", [
            "¿Se requieren certificaciones obligatorias de la empresa adjudicataria?",
            "¿Qué certificaciones obligatorias debe tener la empresa adjudicataria? (Ej. ISO 9001, ISO 14001…)"
        ]),
        (" Seguridad y Protección de Datos", [
            "¿Hay requisitos específicos respecto al cumplimiento de la LOPD/GDPR o el Esquema Nacional de Seguridad?",
            "¿Qué medidas de seguridad se deben implementar durante el tratamiento de los datos?"
        ]),
        (" Auditorías", [
            "¿Se reserva la entidad la posibilidad de realizar auditorías? ¿Sobre qué aspectos?"
        ]),
        (" Contenido de las Ofertas", [
            "¿Qué información debe incluirse en la oferta técnica?",
            "¿Qué información se evaluará mediante fórmula (por ejemplo, precio)?"
        ])
    ]
