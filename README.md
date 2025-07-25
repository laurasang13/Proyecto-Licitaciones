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



| Tipo de Solvencia | Requisito Mínimo Exigido | Medio de Acreditación | Base Legal (LCSP) |
| :---------------- | :----------------------- | :-------------------- | :---------------- |
| **Económica y Financiera** | **Volumen anual de negocios**: Un volumen anual de negocios mínimo de **Noventa Mil Euros (90.000,00 €)** en el ámbito de actividades correspondientes al objeto del contrato, referido al mejor de los tres últimos ejercicios disponibles en función de la fecha de creación o de inicio de las actividades del empresario. | Cuentas anuales aprobadas y depositadas en el Registro Mercantil o en el registro oficial que corresponda, o en su defecto, cualquier otro documento admitido en derecho que acredite el volumen de negocios declarado. Para personas físicas, libros de contabilidad visados. | Art. 87.1.a) |
| | **Seguro de indemnización por riesgos profesionales**: Posesión de un seguro de indemnización por riesgos profesionales por un importe mínimo de cobertura de **Trescientos Mil Euros (300.000,00 €)**, vigente durante todo el periodo de ejecución del contrato y sus posibles prórrogas. | Certificado expedido por el asegurador, en el que consten los importes y riesgos asegurados, así como la fecha de vencimiento de la póliza. Compromiso de renovación si la póliza no cubre la totalidad del periodo. | Art. 87.1.b) |
| **Técnica o Profesional** | **Experiencia en servicios de naturaleza similar**: Una relación de los principales servicios o trabajos realizados en los últimos tres años, que sean de naturaleza o tipología similar al objeto del presente contrato, cuyo importe anual acumulado en el año de mayor ejecución sea igual o superior a **Cuarenta y Cinco Mil Euros (45.000,00 €)**. Se entenderá por servicios de naturaleza similar aquellos relacionados con el mantenimiento, soporte técnico y actualización de sistemas informáticos. | La relación de servicios deberá indicar el importe, la fecha y el destinatario, público o privado. Acreditación mediante certificados expedidos o visados por el órgano competente (sector público) o por el destinatario (sector privado), o declaración del empresario con documentos justificativos. | Art. 89.1.a) |
| | **Personal técnico**: Declaración indicando el personal técnico o las unidades técnicas, estén o no integradas en la empresa, de los que se dispondrá para la ejecución del contrato, especialmente aquellos responsables del control de calidad. | Declaración responsable que incluya el compromiso de adscribir al contrato el personal con la cualificación y experiencia requerida, así como la titulación y experiencia profesional de los perfiles clave que se propongan para la ejecución del servicio. | Art. 89.1.c) |


