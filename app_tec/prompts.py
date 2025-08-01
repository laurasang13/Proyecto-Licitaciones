# Mantenemos tal cual el código del propio pliego técnico
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