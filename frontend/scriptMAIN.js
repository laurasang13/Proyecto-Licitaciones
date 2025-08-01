document.addEventListener('DOMContentLoaded', () => {
    const tenderForm = document.getElementById('tenderForm');
    const tenderResultDiv = document.getElementById('tenderResult');
    const loadingDiv = document.getElementById('loading');

    // Event listeners for conditional display
    document.querySelectorAll('input[name="trata_datos"]').forEach(radio => {
        radio.addEventListener('change', (event) => {
            const subcontrataServidoresDiv = document.getElementById('subcontrata_servidores_div');
            if (event.target.value === 'true') {
                subcontrataServidoresDiv.style.display = 'block';
            } else {
                subcontrataServidoresDiv.style.display = 'none';
                document.getElementById('subcontrata_servidores').value = ''; // Clear input if hidden
            }
        });
    });

    document.querySelectorAll('input[name="subcontratara"]').forEach(radio => {
        radio.addEventListener('change', (event) => {
            const subcontratasNoVinculadasDiv = document.getElementById('subcontratas_no_vinculadas_div');
            if (event.target.value === 'true') {
                subcontratasNoVinculadasDiv.style.display = 'block';
            } else {
                subcontratasNoVinculadasDiv.style.display = 'none';
                document.querySelectorAll('input[name="subcontratas_no_vinculadas"]').forEach(r => r.checked = false); // Uncheck radios
            }
        });
    });

    document.querySelectorAll('input[name="cumple_prtr"]').forEach(radio => {
        radio.addEventListener('change', (event) => {
            const prtrDetailsDiv = document.getElementById('prtr_details_div');
            if (event.target.value === 'true') {
                prtrDetailsDiv.style.display = 'block';
            } else {
                prtrDetailsDiv.style.display = 'none';
                document.querySelectorAll('input[name="modelos_b1b2c"]').forEach(r => r.checked = false);
                document.getElementById('titular_real').value = '';
            }
        });
    });

    document.querySelectorAll('input[name="garantia_provisional"]').forEach(radio => {
        radio.addEventListener('change', (event) => {
            const porcentajeCuantiaDiv = document.getElementById('porcentaje_cuantia_div');
            if (event.target.value === 'true') {
                porcentajeCuantiaDiv.style.display = 'block';
            } else {
                porcentajeCuantiaDiv.style.display = 'none';
                document.getElementById('porcentaje_cuantia').value = '';
            }
        });
    });


    tenderForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        loadingDiv.classList.remove('hidden');
        tenderResultDiv.innerHTML = ''; // Clear previous results

        const formData = new FormData(tenderForm);
        const data = {};

        // Helper to convert string to boolean
        const toBoolean = (value) => value === 'true';

        // Populate the main data object
        data.objeto_contrato = formData.get('objeto_contrato');
        data.necesidad_resuelta = formData.get('necesidad_resuelta');
        data.responsable_contrato = formData.get('responsable_contrato');
        data.lugar_prestacion = formData.get('lugar_prestacion');
        data.pbl_sin_iva = parseFloat(formData.get('pbl_sin_iva'));
        data.iva = parseFloat(formData.get('iva'));
        data.duracion_meses = parseInt(formData.get('duracion_meses'));
        data.prorrogas = parseInt(formData.get('prorrogas'));

        // Documentacion
        data.documentacion = {
            declaracion_responsable: toBoolean(formData.get('declaracion_responsable')),
            oferta_economica: toBoolean(formData.get('oferta_economica')),
            aceptacion_pliego: toBoolean(formData.get('aceptacion_pliego')),
            equipo_cumple: toBoolean(formData.get('equipo_cumple')),
            fecha: formData.get('fecha')
        };
        console.log("Oferta económica: ", data.documentacion); // Debugging log
        // ProteccionDatos
        const trataDatos = toBoolean(formData.get('trata_datos'));
        data.proteccion_datos = {
            trata_datos: trataDatos,
            subcontrata_servidores: trataDatos ? formData.get('subcontrata_servidores') || null : null
        };

        // Subcontratacion
        const subcontratara = toBoolean(formData.get('subcontratara'));
        data.subcontratacion = {
            subcontratara: subcontratara,
            subcontratas_no_vinculadas: subcontratara ? toBoolean(formData.get('subcontratas_no_vinculadas')) : null
        };

        // CriteriosValoracion
        data.criterios = {
            precio_ofertado: parseFloat(formData.get('precio_ofertado')),
            anormalmente_bajo: toBoolean(formData.get('anormalmente_bajo'))
        };

        // NextGeneration
        const cumplePrtr = toBoolean(formData.get('cumple_prtr'));
        data.nextgen = {
            cumple_prtr: cumplePrtr,
            modelos_b1b2c: cumplePrtr ? toBoolean(formData.get('modelos_b1b2c')) : null,
            titular_real: cumplePrtr ? formData.get('titular_real') || null : null
        };

        // Garantias
        const garantiaProvisional = toBoolean(formData.get('garantia_provisional'));
        data.garantias = {
            garantia_provisional: garantiaProvisional,
            porcentaje_cuantia: garantiaProvisional ? formData.get('porcentaje_cuantia') || null : null
        };

        // Solvencia
        data.solvencia = {
            volumen_anual_negocios_min: parseFloat(formData.get('volumen_anual_negocios_min')),
            importe_anual_similares_min: parseFloat(formData.get('importe_anual_similares_min')),
            seguro_rcp_min: parseFloat(formData.get('seguro_rcp_min'))
        };

        // Ponderacion
        console.log("Valor RAW de 'metodologia_plan':", formData.get('metodologia_plan'));
        console.log("Valor RAW de 'equipo_experiencia':", formData.get('equipo_experiencia'));
        console.log("Valor RAW de 'dnsh_sostenibilidad':", formData.get('dnsh_sostenibilidad'));
        console.log("Valor RAW de 'oferta_economica':", formData.get('oferta_economica')); // <-- ¡Este es el clave!


        data.ponderacion = {
            metodologia_plan: parseFloat(formData.get('metodologia_plan')),
            equipo_experiencia: parseFloat(formData.get('equipo_experiencia')),
            dnsh_sostenibilidad: parseFloat(formData.get('dnsh_sostenibilidad')),
            oferta_economica: parseFloat(formData.get('oferta_economica'))
        };

        const metodologiaPlan = data.ponderacion.metodologia_plan || 0;
        const equipoExperiencia = data.ponderacion.equipo_experiencia || 0;
        const dnshSostenibilidad = data.ponderacion.dnsh_sostenibilidad || 0;
        const ofertaEconomica = data.ponderacion.oferta_economica || 0;

        const sumaPonderacion = metodologiaPlan + equipoExperiencia + dnshSostenibilidad + ofertaEconomica;

        // Usamos una pequeña tolerancia para evitar problemas de coma flotante
        if (Math.abs(sumaPonderacion - 100) > 0.01) { // Por ejemplo, 0.01 de tolerancia
            alert(`La suma de los porcentajes de criterios es ${sumaPonderacion.toFixed(2)}%, debe ser exactamente 100%. Por favor, ajústelos.`);
            loadingDiv.classList.add('hidden'); // Oculta el cargando si estaba visible
            return; // Detiene el envío del formulario
        }

        console.log("Sending data:", data); // Log data to be sent

        try {
            console.log(data)

            const response = await fetch('http://127.0.0.1:8000/administrativo', { // Replace with your FastAPI URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Server error:", errorData);
                throw new Error(`HTTP error! status: ${response.status} - ${JSON.stringify(errorData)}`);
            }

            const result = await response.json();
            console.log("Received result:", result);
            tenderResultDiv.innerHTML = `<h2>Pliego Generado:</h2><pre>${result.pliego_final}</pre>`;

        } catch (error) {
            console.error('Error generating tender:', error);
            tenderResultDiv.innerHTML = `<p class="error">Error al generar el pliego: ${error.message}. Por favor, revise los datos e inténtelo de nuevo.</p>`;
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });
});