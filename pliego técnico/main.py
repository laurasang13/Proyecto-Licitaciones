# from utils import inicializar_gemini, obtener_preguntas
# from prompts import generar_prompt_por_seccion

# def obtener_respuestas(preguntas):
#     respuestas = {}
#     print("Responde a las siguientes preguntas para generar el pliego técnico por secciones:\n")
#     for titulo, subpreguntas in preguntas:
#         print(f"\n🟨 {titulo}")
#         seccion_respuestas = {}
#         for pregunta in subpreguntas:
#             respuesta = input(f"{pregunta} ")
#             seccion_respuestas[pregunta] = respuesta
#         respuestas[titulo] = seccion_respuestas
#     return respuestas

# def main():
#     modelo = inicializar_gemini()
#     preguntas = obtener_preguntas()
#     respuestas = obtener_respuestas(preguntas)

#     print("\n\n🧾 GENERANDO PLIEGO TÉCNICO POR SECCIONES...\n")

#     secciones_redactadas = {}
#     for titulo, contenido in respuestas.items():
#         print(f"✍️ Generando sección: {titulo}...")
#         prompt = generar_prompt_por_seccion(titulo, contenido)
#         respuesta = modelo.generate_content(prompt)
#         secciones_redactadas[titulo] = respuesta.text

#     print("\n\n📄 PLIEGO TÉCNICO COMPLETO:\n")
#     for numero, (titulo, contenido) in enumerate(secciones_redactadas.items(), start=1):
#         print(f"{numero}. {titulo.upper()}\n")
#         print(contenido)
#         print("\n" + "-"*80 + "\n")
    

# if __name__ == "__main__":
#     main()

from utils import inicializar_gemini, obtener_preguntas
from prompts import generar_prompt_por_seccion

def obtener_respuestas(preguntas):
    respuestas = {}
    print("Responde a las siguientes preguntas para generar el pliego técnico por secciones:\n")
    for titulo, subpreguntas in preguntas:
        print(f"\n🟨 {titulo}")
        seccion_respuestas = {}
        saltar_restantes = False

        for pregunta in subpreguntas:
            if not saltar_restantes:
                respuesta = input(f"{pregunta} ")
                seccion_respuestas[pregunta] = respuesta

                # Lógica para saltar preguntas si la respuesta es "no"
                if "¿se requieren" in pregunta.lower() and respuesta.strip().lower().startswith("no"):
                    saltar_restantes = True

        respuestas[titulo] = seccion_respuestas
    return respuestas

def main():
    modelo = inicializar_gemini()
    preguntas = obtener_preguntas()
    respuestas = obtener_respuestas(preguntas)

    print("\n\n🧾 GENERANDO PLIEGO TÉCNICO POR SECCIONES...\n")

    secciones_redactadas = {}
    for titulo, contenido in respuestas.items():
        print(f"✍️ Generando sección: {titulo}...")
        prompt = generar_prompt_por_seccion(titulo, contenido)
        respuesta = modelo.generate_content(prompt)
        secciones_redactadas[titulo] = respuesta.text

    # Obtener el objeto del contrato para ponerlo en el título
    objeto_pregunta = "¿Cuál es el objeto principal del contrato? (por ejemplo: escaneo de documentos, desarrollo de software, suministro de material…)"
    objeto = respuestas[" Objeto del Contrato"].get(objeto_pregunta, "").capitalize()

    # Añadir título del pliego
    print(f"\n\n📘 PLIEGO TÉCNICO PARA LICITACIÓN PÚBLICA: {objeto}\n")

    # Generar índice
    print("📑 ÍNDICE\n")
    for numero, titulo in enumerate(secciones_redactadas.keys(), start=1):
        partes = titulo.split(". ", 1)
        titulo_limpio = partes[1].capitalize() if len(partes) > 1 else titulo.capitalize()
        print(f"{numero}. {titulo_limpio}")
    print("\n" + "="*80 + "\n")

    for numero, (titulo, contenido) in enumerate(secciones_redactadas.items(), start=1):
        print(f"{numero}. {titulo.upper()}\n")
        print(contenido)
        print("\n" + "-"*80 + "\n")
    

if __name__ == "__main__":
    main()

