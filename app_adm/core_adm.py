# app/admin_core.py

from .model_adm import Datos
from .LiciZen_adm import redactar_secciones, REVISION_FINAL, SECCIONES, llm


async def generar_pliego_administrativo(datos: Datos) -> dict:
    """
    Procesa los datos enviados por el usuario, redacta cada sección del pliego administrativo,
    y devuelve un diccionario con la información estructurada.
    """
    # Generar todas las secciones (async)
    secciones = await redactar_secciones(datos)

    # Unir las secciones en texto completo en markdown
    texto_completo = "\n\n".join(f"## {titulo}\n\n{contenido}" for titulo, contenido in secciones.items())

    # Aplicar revisión final con modelo Gemini
    revisado = REVISION_FINAL | llm
    pliego_final = revisado.invoke({"pliego": texto_completo}).content

    return {
        "objeto": datos.objeto_contrato,
        "indice": list(secciones.keys()),
        "secciones": secciones,
        "pliego_final": pliego_final
    }
