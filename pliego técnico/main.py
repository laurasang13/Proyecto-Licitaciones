# from utils import inicializar_gemini, obtener_preguntas
# from prompts import generar_prompt

# def obtener_respuestas(preguntas):
#     respuestas = {}
#     print("Responde a las siguientes preguntas para generar el pliego técnico:\n")
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
#     prompt = generar_prompt(respuestas)
#     resultado = modelo.generate_content(prompt)
    
#     print("\n\n🧾 PLIEGO TÉCNICO GENERADO:\n")
#     print(resultado.text)

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
        for pregunta in subpreguntas:
            respuesta = input(f"{pregunta} ")
            seccion_respuestas[pregunta] = respuesta
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

    print("\n\n📄 PLIEGO TÉCNICO COMPLETO:\n")
    for numero, (titulo, contenido) in enumerate(secciones_redactadas.items(), start=1):
        print(f"{numero}. {titulo.upper()}\n")
        print(contenido)
        print("\n" + "-"*80 + "\n")

if __name__ == "__main__":
    main()

