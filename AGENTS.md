# Proyecto: Comparador de Reglas Procesales - PEJENP

## Propósito
Aplicación Streamlit local para comparar actos procesales y transiciones por órgano jurisdiccional, bandeja, tarea de origen y motivo de ingreso. Mantener trazabilidad de filas originales del Excel.

## Reglas obligatorias para cambios de código
1. No modificar los datos Excel originales ni sobrescribir la matriz cargada.
2. Hoja origen: `PROCESO ÚNICO`, segunda fila de encabezados, datos desde fila 3.
3. Preservar la trazabilidad de `fila_excel`.
4. Ausencia en una tarea y diferencias de transición son HALLAZGOS, no errores confirmados.
5. Comparar actos solo dentro del mismo motivo de ingreso y del contexto procesal filtrado.
6. Distinguir `PENDIENTE` exacto de un estado válido como `EN TRAMITE(PENDIENTE)`.
7. No leer, abrir, adjuntar ni sincronizar Excel institucional mientras se usa Codex sin autorización. Un agente puede enviar contenido analizado a sus servicios; desarrollar con datos sintéticos. No publicar repositorios con datos institucionales.
8. Priorizar pruebas unitarias de `matrix_core.py` y pruebas de integración con Excel.
9. Mantener accesible la app en Windows y el texto de interfaz en español.
10. Documentar cambios y ejecutar `python -m pytest -q` antes de declarar listo.

## Estructura
- `app.py`: interfaz Streamlit.
- `matrix_core.py`: validación, importación y cálculos de comparación.
- `tests/`: pruebas.
- `data/matriz_proceso_unico.xlsx`: documento opcional de prueba local, excluido por .gitignore. El ZIP de código no contiene el Excel.

## Próximas mejoras acordadas (no implementar sin autorización)
- Registro de observaciones, acuerdos y validaciones durante reuniones.
- Reglas de comparación enriquecidas por sentido de calificación, fallo y audiencia.
- Exportación de reportes e importación de múltiples versiones para control de cambios.
