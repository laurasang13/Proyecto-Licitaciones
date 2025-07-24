# Proyecto Automatización de Licitaciones de Servicios Profesionales

## 📋 Descripción

Este proyecto tiene como objetivo automatizar la búsqueda, descarga, extracción y procesamiento de licitaciones de servicios profesionales publicadas en fuentes oficiales como el BOE y la Plataforma de Contratación del Estado. Además, genera documentos base personalizados para facilitar la preparación de ofertas.

---

## 🚀 Funcionalidades principales

- Búsqueda automatizada de licitaciones filtrando por palabras clave (ej. "servicios", "formación", "marketing").
- Descarga masiva y extracción de texto de los pliegos en formato PDF.
- Procesamiento de texto para extraer fechas límite, requisitos y documentación necesaria mediante técnicas de NLP.
- Generación automática de documentos base (Word/PDF) rellenados con la información clave extraída.
- Interfaz web sencilla (Streamlit) para búsqueda, visualización y generación de documentos.

---

## 🗂️ Estructura del proyecto

- scraping/ # Scripts para búsqueda y descarga de licitaciones

- extraction/ # Scripts para extracción y limpieza de texto de PDFs

- nlp_processing/ # Scripts para procesamiento NLP y extracción de datos clave

- doc_generation/ # Plantillas y scripts para generación de documentos base

- interface/ # Código de la aplicación Streamlit

- tests/ # Pruebas unitarias y de integración

- requirements.txt # Dependencias del proyecto

- README.md # Este archivo

- LICENSE # Licencia del proyecto


---

## 📅 Planificación

El proyecto se organiza en etapas secuenciales:

| Etapa                         | Descripción                                   | Fechas           |
|-------------------------------|-----------------------------------------------|------------------|
| 1. Scraping y API             | Búsqueda y descarga de licitaciones           | 11 - 15 julio    |
| 2. Descarga y extracción      | Descarga de PDFs y extracción de texto        | 16 - 18 julio    |
| 3. Procesamiento NLP          | Extracción de fechas, requisitos y documentación | 21 - 23 julio    |
| 4. Generación de documentos   | Creación automática de documentos base         | 24 - 25 julio    |
| 5. Desarrollo de interfaz     | Construcción de la app Streamlit                | 28 - 30 julio    |
| 6. Pruebas y documentación   | Testeo final, corrección y documentación        | 31 julio         |

| Criterio de Adjudicación                                            | Ponderación (%) | Naturaleza de la Evaluación |
| :------------------------------------------------------------------ | :-------------- | :-------------------------- |
| Metodología y Plan de Trabajo                                       | 30%             | Juicio de valor             |
| Experiencia y Cualificación del Equipo Adscrito                     | 20%             | Juicio de valor             |
| Medidas para el cumplimiento del principio DNSH y Sostenibilidad    | 10%             | Juicio de valor             |
| Oferta Económica (Precio Ofertado)                                  | 40%             | Automática                  |
| **Total**                                                           | **100%**        |                             |




