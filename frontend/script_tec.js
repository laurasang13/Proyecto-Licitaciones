document.addEventListener('DOMContentLoaded', () => {
    // --- Referencias a elementos del DOM ---
    const tecTenderForm = document.getElementById('tecTenderForm');
    const questionsContainer = document.getElementById('questionsContainer');
    const tenderResultDiv = document.getElementById('tenderResult'); // Para mensajes
    const loadingDiv = document.getElementById('loading');

    // --- URLs de las APIs Técnicas ---
    const TEC_QUESTIONS_API_URL = 'http://127.0.0.1:8001/preguntas'; // Tu API técnica para preguntas
    const TEC_GENERATE_API_URL = 'http://127.0.0.1:8001/generar';   // Tu API técnica para generar

    let technicalQuestions = []; // Para almacenar las preguntas obtenidas de la API

    // --- Función para cargar las preguntas dinámicamente ---
    async function loadTechnicalQuestions() {
        loadingDiv.classList.remove('hidden');
        questionsContainer.innerHTML = ''; // Limpiar preguntas anteriores
        tenderResultDiv.innerHTML = ''; // Limpiar mensajes anteriores

        try {
            const response = await fetch(TEC_QUESTIONS_API_URL);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error! status: ${response.status} - ${JSON.stringify(errorData)}`);
            }
            technicalQuestions = await response.json();
            console.log("Preguntas técnicas cargadas:", technicalQuestions);

            // Construir el formulario dinámicamente
            technicalQuestions.forEach(section => {
                const sectionTitle = section[0];
                const questions = section[1];

                const fieldset = document.createElement('fieldset');
                const legend = document.createElement('legend');
                legend.textContent = sectionTitle.replace(/^\s+|\s+$/g, ''); // Eliminar espacios iniciales/finales
                fieldset.appendChild(legend);

                questions.forEach((question, index) => {
                    // CASO ESPECIAL: Primera pregunta condicional (Ahora con Radio Buttons)
                    if (question.trim() === "¿Se requieren certificaciones obligatorias de la empresa adjudicataria?") {
                        const questionDiv = document.createElement('div'); // Contenedor para la pregunta y sus radios
                        questionDiv.classList.add('radio-group-container'); // Para posible estilizado CSS

                        const labelText = document.createElement('label');
                        labelText.textContent = question;
                        questionDiv.appendChild(labelText);

                        // Radio Button "Sí"
                        const radioYes = document.createElement('input');
                        radioYes.type = 'radio';
                        radioYes.id = `${sectionTitle}__${index}_yes`;
                        radioYes.name = `${sectionTitle}__${index}`; // Mismo nombre para el grupo de radios
                        radioYes.value = 'Sí';
                        radioYes.required = true;

                        const labelYes = document.createElement('label');
                        labelYes.setAttribute('for', radioYes.id);
                        labelYes.textContent = 'Sí';

                        // Radio Button "No"
                        const radioNo = document.createElement('input');
                        radioNo.type = 'radio';
                        radioNo.id = `${sectionTitle}__${index}_no`;
                        radioNo.name = `${sectionTitle}__${index}`; // Mismo nombre para el grupo de radios
                        radioNo.value = 'No';
                        radioNo.required = true;

                        const labelNo = document.createElement('label');
                        labelNo.setAttribute('for', radioNo.id);
                        labelNo.textContent = 'No';

                        questionDiv.appendChild(radioYes);
                        questionDiv.appendChild(labelYes);
                        questionDiv.appendChild(radioNo);
                        questionDiv.appendChild(labelNo);

                        fieldset.appendChild(questionDiv);

                        // Escuchar cambios en los radio buttons
                        const handleRadioChange = () => {
                            const valor = radioYes.checked ? 'Sí' : (radioNo.checked ? 'No' : '');

                            // Eliminar cualquier pregunta anterior dependiente
                            const existentes = fieldset.querySelectorAll('.cert-question');
                            existentes.forEach(el => el.remove());

                            if (valor === 'Sí') {
                                // Crear segunda pregunta solo si se selecciona "Sí"
                                const secondLabel = document.createElement('label');
                                secondLabel.textContent = "¿Qué certificaciones obligatorias debe tener la empresa adjudicataria? (Ej. ISO 9001, ISO 14001…)";
                                secondLabel.classList.add('cert-question');

                                const secondTextarea = document.createElement('textarea');
                                secondTextarea.name = `${sectionTitle}__certificaciones`; // Nuevo nombre para esta pregunta
                                secondTextarea.rows = 3;
                                secondTextarea.required = true;
                                secondTextarea.classList.add('cert-question');

                                fieldset.appendChild(secondLabel);
                                fieldset.appendChild(secondTextarea);
                            }
                        };

                        radioYes.addEventListener('change', handleRadioChange);
                        radioNo.addEventListener('change', handleRadioChange);

                    } else {
                        // Resto de preguntas normales (textarea)
                        const label = document.createElement('label');
                        label.textContent = question;

                        const inputName = `${sectionTitle}__${index}`;
                        const inputElement = document.createElement('textarea');
                        inputElement.name = inputName;
                        inputElement.rows = 3;
                        inputElement.required = true;

                        fieldset.appendChild(label);
                        fieldset.appendChild(inputElement);
                    }
                });

                questionsContainer.appendChild(fieldset);
            });

        } catch (error) {
            console.error('Error al cargar las preguntas técnicas:', error);
            tenderResultDiv.innerHTML = `<p class="error">Error al cargar las preguntas técnicas: ${error.message}</p>`;
        } finally {
            loadingDiv.classList.add('hidden');
        }
    }

    // --- Lógica para enviar el formulario técnico ---
    tecTenderForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        loadingDiv.classList.remove('hidden');
        tenderResultDiv.innerHTML = ''; // Limpiar mensajes

        const formData = new FormData(tecTenderForm);
        const respuestas = {}; // Esto será Dict[str, Dict[str, str]]

        // Iterar sobre las preguntas técnicas cargadas para reconstruir la estructura de `respuestas`
        technicalQuestions.forEach(section => {
            const sectionTitle = section[0];
            const questions = section[1];
            respuestas[sectionTitle] = {};

            questions.forEach((question, index) => {
                let answer = null;
                if (question.trim() === "¿Se requieren certificaciones obligatorias de la empresa adjudicataria?") {
                    const radioGroupName = `${sectionTitle}__${index}`;
                    answer = formData.get(radioGroupName);

                    if (answer === 'Sí') {
                        const certAnswer = formData.get(`${sectionTitle}__certificaciones`);
                        if (certAnswer !== null) {
                            respuestas[sectionTitle]["¿Qué certificaciones obligatorias debe tener la empresa adjudicataria? (Ej. ISO 9001, ISO 14001…)"] = certAnswer;
                        }
                    }
                    respuestas[sectionTitle][question] = answer;
                } else {
                    const inputName = `${sectionTitle}__${index}`;
                    answer = formData.get(inputName);
                    if (answer !== null) {
                        respuestas[sectionTitle][question] = answer;
                    }
                }
            });
        });

        const requestPayload = {
            respuestas: respuestas
        };

        console.log("Enviando datos técnicos:", requestPayload);

        try {
            const response = await fetch(TEC_GENERATE_API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestPayload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Error del servidor (API Técnica):", errorData);
                throw new Error(`¡Error HTTP! Estado: ${response.status} - ${JSON.stringify(errorData)}`);
            }

            const result = await response.json();
            console.log("Resultado técnico recibido:", result);
            // --- Construir el contenido en Markdown para el editor ---
            let editorContent = `## Pliego Técnico Generado (${result.objeto}):\n\n`;
            editorContent += `### Índice:\n`;
            result.indice.forEach(item => {
                editorContent += `- ${item}\n`;
            });
            editorContent += `\n`;

            // Verifica si ya hay encabezados en el contenido generado
            for (const sectionTitle in result.secciones) {
                const contenido = result.secciones[sectionTitle];

                // Si ya contiene un encabezado tipo '### ', no lo duplicamos
                const tieneEncabezado = contenido.trim().startsWith('#');

                if (!tieneEncabezado) {
                    editorContent += `### ${sectionTitle.trim()}\n\n`;
                }

                editorContent += `${contenido}\n\n`;
            }

            
            // --- Guardar el contenido en localStorage y redirigir ---
            localStorage.setItem('generatedPliegoContent', editorContent);
            window.location.href = 'editor.html'; // Redirige a la nueva página del editor
            console.log("Redirigiendo al editor con el contenido generado.");

        } catch (error) {
            console.error('Error al generar el pliego técnico:', error);
            tenderResultDiv.innerHTML = `<p class="error">Error al generar el pliego técnico: ${error.message}. Por favor, revise los datos e inténtelo de nuevo.</p>`;
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });

    // Cargar las preguntas técnicas al cargar la página
    loadTechnicalQuestions();
});