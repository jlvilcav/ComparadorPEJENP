# Solicitud de revisión y mejora para Codex

Actúa como desarrollador senior de Python/Streamlit y analista funcional de sistemas judiciales. Trabaja sobre **la carpeta abierta** que contiene `app.py`, `matrix_core.py`, `tests/`, `AGENTS.md` y `data/`.

## Objetivo
Mantener y mejorar el **Comparador de Actos Procesales y Transiciones Procesales del PEJENP**, implementado con Python + Streamlit, de acuerdo con el comportamiento V2: filtros de especialidad, subespecialidad, nivel de instancia, órgano jurisdiccional, bandeja de origen, selección múltiple de tareas y filtro de **un mismo motivo de ingreso**. Mostrar actos comunes, actos ausentes y diferencias de transiciones (estado de origen, estado destino, bandeja destino, tarea destino), indicadores por campo, detalle y exportación.

## Instrucciones
1. Lee `README.md`, `AGENTS.md` y el código fuente **antes de modificar**.
2. Ejecuta los tests existentes y revisa errores. Para la carga Excel utiliza un archivo de datos sintéticos. No accedas al Excel institucional salvo que el usuario lo autorice expresamente.
3. Mantén la matriz original en modo solo lectura y las referencias a `fila_excel`.
4. Los actos que aparecen en solo una tarea son **diferencias para validación**, no errores procesales confirmados.
5. Conserva la distinción entre el valor `PENDIENTE` y un estado real con esa palabra dentro de su nombre.
6. Utiliza exclusivamente ejemplos sintéticos para las pruebas.
7. Mejora la interfaz visual con tablas comparativas de actos en columnas por tarea, posibilidad de ver el destino de cada acto y filtros de hallazgos.
8. Mantén la lógica central en `matrix_core.py` y agrega o actualiza pruebas automatizadas.
9. Primero presenta tu plan de cambios, después implementa y ejecuta las pruebas. No declares completado lo que no hayas comprobado.
10. **Confidencialidad:** usa únicamente datos sintéticos o anonimizados para tu trabajo. No abras ni leas la matriz institucional sin autorización. No publiques el proyecto con datos de trabajo.

## Prioridad
Comienza validando que la aplicación arranca en Windows con datos sintéticos. Luego mejora la presentación lado a lado de los actos y transiciones. Evita reescribir desde cero si el proyecto ya funciona.
