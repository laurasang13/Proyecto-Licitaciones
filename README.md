$$Puntuación_{económica} = \frac{Precio_{mínimo\;ofertado}}{Precio_{oferta\;evaluada}} \times 30$$

Donde:
*   $Precio_{mínimo\;ofertado}$: Es el precio más bajo de entre todas las ofertas económicas válidamente admitidas.
*   $Precio_{oferta\;evaluada}$: Es el precio de la oferta económica que se está evaluando.



# LiciZen — Asistente Inteligente para Redacción de Licitaciones Públicas

**LicitaIA** es un asistente basado en inteligencia artificial diseñado para automatizar la generación de pliegos técnicos y administrativos en licitaciones públicas. El objetivo es facilitar la participación de empresas en concursos públicos, reduciendo errores y tiempo de redacción, a través de un sistema conversacional inteligente.

---

## Objetivos del Proyecto

- Redacción automatizada de pliegos técnicos y administrativos conforme a las normativas.
- Asistente conversacional capaz de recoger información clave de la empresa y del contrato mediante preguntas.
- Base de conocimiento entrenada con documentos reales para ofrecer propuestas contextualizadas y adecuadas.
- Interfaz web amigable, con posibilidad de integrarse en portales de gestión o CRMs.
- Exportación de los documentos generados en formatos compatibles: `.docx`, `.pdf`, `.json`.

---

## Estado actual del proyecto

- Redacción automática del **pliego administrativo** a partir de una plantilla estructurada.
- Asistente conversacional con flujo predefinido para generar el **pliego técnico**.
- Uso de modelos de lenguaje (Gemini / GPT) conectados vía API con claves en `.env`.
- Interfaz funcional (CLI y/o web) para pruebas locales.
- Separación modular del código: carga de prompts, gestión de variables, conexión con LLMs.

---

## Próximos pasos

- Incluir **memorias técnicas completas** personalizables según sector.
- Ingesta de documentos (PDFs, DOCX) con **extracción automática de información clave**.
- Implementación de un sistema de **RAG** (Retrieval-Augmented Generation) para responder preguntas sobre normativas y adaptar los pliegos automáticamente.
- Generación de documentos adaptados a **diferentes organismos públicos** (cabildos, ayuntamientos, gobierno autonómico...).
- Registro de usuarios y almacenamiento seguro de respuestas para reutilización futura.
- Implementación de firmas digitales o validaciones oficiales (en fases futuras).

---

## 🛠Tecnologías utilizadas

- `Python 3.10+`
- `Langchain`, `Ollama` / `OpenAI` / `Gemini API`
- `Streamlit` (para interfaz web)
- `dotenv`, `PyPDF2`, `docx`, `Jinja2`
- `Git` + `GitHub` para control de versiones

---

## Estructura del repositorio
LiciZen

├── main.py # Lógica principal del asistente

├── prompts/ # Plantillas de preguntas y redacciones

├── templates/ # Pliegos base y estructuras .docx / .jinja

├── utils/ # Funciones auxiliares

├── .env.example # Variables de entorno (sin claves)

├── requirements.txt # Dependencias del proyecto

└── README.md # Este documento


