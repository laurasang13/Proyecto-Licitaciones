# def generar_prompt(respuestas):
#     prompt = "Redacta un pliego técnico detallado y profesional basado en las siguientes respuestas del usuario:\n\n"
    
#     for seccion, pares in respuestas.items():
#         prompt += f"## {seccion} ##\n"
#         for pregunta, respuesta in pares.items():
#             prompt += f"- {pregunta}\n  {respuesta}\n"
#         prompt += "\n"
#     prompt += (
#         "Redáctalo siguiendo la estructura habitual de un pliego técnico oficial, "
#         "en lenguaje administrativo, con claridad, orden y precisión."
#     )
#     return prompt

# def generar_prompt(respuestas):
#     prompt = (
#         "Eres un experto en contratación pública. A partir de las siguientes respuestas del usuario, redacta un pliego técnico detallado y profesional, "
#         "siguiendo rigurosamente el formato de un pliego oficial. El resultado debe tener la siguiente estructura obligatoria:\n\n"
#         "1. TÍTULO: Un título claro y formal para el pliego técnico.\n"
#         "2. ÍNDICE: Lista numerada con todos los apartados principales del pliego.\n"
#         "3. CONTENIDO: Desarrollo de cada sección (de la 1 a la 12) siguiendo exactamente los títulos indicados por el usuario.\n\n"
#         "En cada sección del contenido:\n"
#         "- Desarrolla ampliamente los puntos aportados.\n"
#         "- Usa un lenguaje técnico y administrativo.\n"
#         "- No repitas las preguntas textualmente, conviértelas en un texto fluido y coherente.\n"
#         "- Usa subtítulos o párrafos si el contenido lo requiere.\n"
#         "- Mantén el número y título exacto de cada sección.\n\n"
#         "Respuestas del usuario:\n\n"
#     )

#     for seccion, pares in respuestas.items():
#         prompt += f"## {seccion} ##\n"
#         for pregunta, respuesta in pares.items():
#             prompt += f"- {pregunta}\n  {respuesta}\n"
#         prompt += "\n"

#     prompt += (
#         "\nRedacta el pliego completo respetando la estructura indicada, incluyendo título general, índice y secciones numeradas. "
#         "Escribe con claridad, profesionalismo y detalle, como si fuera a ser presentado en una licitación oficial."
#     )

#     return prompt

def generar_prompt_por_seccion(titulo_seccion, pares):
    prompt = (
        f"Eres un experto en redacción de pliegos técnicos para licitaciones públicas. "
        f"Redacta de forma detallada, formal y profesional el contenido correspondiente a la sección '{titulo_seccion}' "
        f"a partir de las siguientes respuestas del usuario:\n\n"
    )

    for pregunta, respuesta in pares.items():
        prompt += f"- {pregunta}\n  {respuesta}\n"

    prompt += (
        f"\nRedacta un texto fluido y técnico sobre esta sección titulada '{titulo_seccion}'. "
        f"No repitas las preguntas, convierte el contenido en texto claro, estructurado y extenso. "
        f"Respeta el tono administrativo y profesional habitual en un pliego técnico."
    )

    return prompt
