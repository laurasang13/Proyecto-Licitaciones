document.addEventListener('DOMContentLoaded', () => {
    const tenderForm = document.getElementById('tenderForm');
    const tenderResultDiv = document.getElementById('tenderResult');
    const loadingDiv = document.getElementById('loading');

    // Mostrar/ocultar campos condicionales
    document.querySelectorAll('input[name="trata_datos"]').forEach(radio => {
        radio.addEventListener('change', (event) => {
            const subcontrataServidoresDiv = document.getElementById('subcontrata_servidores_div');
            subcontrataServidoresDiv.style.display = event.target.value === 'true' ? 'block' : 'none';
            if (event.target.value !== 'true') document.getElementById('subcontrata_servidores').value = '';
        });
    });

    document.querySelectorAll('input[name="subcontratara"]').forEach(radio => {
        radio.addEventListener('change', (event) => {
            const div = document.getElementById('subcontratas_no_vinculadas_div');
            div.style.display = event.target.value === 'true' ? 'block' : 'none';
            if (event.target.value !== 'true') {
                document.querySelectorAll('input[name="subcontratas_no_vinculadas"]').forEach(r => r.checked = false);
            }
        });
    });

    document.querySelectorAll('input[name="cumple_prtr"]').forEach(radio => {
        radio.addEventListener('change', (event) => {
            const div = document.getElementById('prtr_details_div');
            div.style.display = event.target.value === 'true' ? 'block' : 'none';
            if (event.target.value !== 'true') {
                document.querySelectorAll('input[name="modelos_b1b2c"]').forEach(r => r.checked = false);
                document.getElementById('titular_real').value = '';
            }
        });
    });

    document.querySelectorAll('input[name="garantia_provisional"]').forEach(radio => {
        radio.addEventListener('change', (event) => {
            const div = document.getElementById('porcentaje_cuantia_div');
            div.style.display = event.target.value === 'true' ? 'block' : 'none';
            if (event.target.value !== 'true') document.getElementById('porcentaje_cuantia').value = '';
        });
    });

    tenderForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        loadingDiv.classList.remove('hidden');
        tenderResultDiv.innerHTML = '';

        const formData = new FormData(tenderForm);
        const toBoolean = value => value === 'true';

        const data = {
            objeto_contrato: formData.get('objeto_contrato'),
            necesidad_resuelta: formData.get('necesidad_resuelta'),
            responsable_contrato: formData.get('responsable_contrato'),
            lugar_prestacion: formData.get('lugar_prestacion'),
            pbl_sin_iva: parseFloat(formData.get('pbl_sin_iva')),
            iva: parseFloat(formData.get('iva')),
            duracion_meses: parseInt(formData.get('duracion_meses')),
            prorrogas: parseInt(formData.get('prorrogas')),
            documentacion: {
                declaracion_responsable: toBoolean(formData.get('declaracion_responsable')),
                oferta_economica: toBoolean(formData.get('oferta_economica')),
                aceptacion_pliego: toBoolean(formData.get('aceptacion_pliego')),
                equipo_cumple: toBoolean(formData.get('equipo_cumple')),
                fecha: formData.get('fecha')
            },
            proteccion_datos: {
                trata_datos: toBoolean(formData.get('trata_datos')),
                subcontrata_servidores: toBoolean(formData.get('trata_datos')) ? formData.get('subcontrata_servidores') || null : null
            },
            subcontratacion: {
                subcontratara: toBoolean(formData.get('subcontratara')),
                subcontratas_no_vinculadas: toBoolean(formData.get('subcontratara')) ? toBoolean(formData.get('subcontratas_no_vinculadas')) : null
            },
            criterios: {
                precio_ofertado: parseFloat(formData.get('precio_ofertado')),
                anormalmente_bajo: toBoolean(formData.get('anormalmente_bajo'))
            },
            nextgen: {
                cumple_prtr: toBoolean(formData.get('cumple_prtr')),
                modelos_b1b2c: toBoolean(formData.get('cumple_prtr')) ? toBoolean(formData.get('modelos_b1b2c')) : null,
                titular_real: toBoolean(formData.get('cumple_prtr')) ? formData.get('titular_real') || null : null
            },
            garantias: {
                garantia_provisional: toBoolean(formData.get('garantia_provisional')),
                porcentaje_cuantia: toBoolean(formData.get('garantia_provisional')) ? formData.get('porcentaje_cuantia') || null : null
            },
            solvencia: {
                volumen_anual_negocios_min: parseFloat(formData.get('volumen_anual_negocios_min')),
                importe_anual_similares_min: parseFloat(formData.get('importe_anual_similares_min')),
                seguro_rcp_min: parseFloat(formData.get('seguro_rcp_min'))
            },
            ponderacion: {
                metodologia_plan: parseFloat(formData.get('metodologia_plan')),
                equipo_experiencia: parseFloat(formData.get('equipo_experiencia')),
                dnsh_sostenibilidad: parseFloat(formData.get('dnsh_sostenibilidad')),
                oferta_economica: parseFloat(formData.get('oferta_economica'))
            }
        };

        const sumaPonderacion = Object.values(data.ponderacion).reduce((a, b) => a + b, 0);
        if (Math.abs(sumaPonderacion - 100) > 0.01) {
            alert(`La suma de los porcentajes de criterios es ${sumaPonderacion.toFixed(2)}%. Debe ser exactamente 100%.`);
            loadingDiv.classList.add('hidden');
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/administrativo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error ${response.status} - ${JSON.stringify(errorData)}`);
            }

            const result = await response.json();
            console.log("Pliego recibido:", result.pliego_final);

            // --- Guardar el contenido en localStorage y redirigir ---
            localStorage.setItem('generatedPliegoContent', result.pliego_final);
            window.location.href = 'editor.html';
            console.log("Redirigiendo al editor con el contenido generado.");

        } catch (error) {
            console.error('Error al generar el pliego administrativo:', error);
            tenderResultDiv.innerHTML = `<p class="error">Error al generar el pliego: ${error.message}</p>`;
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });
});
