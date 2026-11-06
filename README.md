# Comparador de Actos Procesales y Transiciones — PEJENP V2

Esta es la implementación en **Python + Streamlit** de la comparación por motivo de ingreso, tarea de origen, actos procesales y transiciones. A diferencia del HTML estático, permite seleccionar nuevos Excel .xlsx.

## ¿Qué es Streamlit?

Streamlit es una biblioteca de Python para construir aplicaciones con formularios, filtros, tablas y métricas que se visualizan en Chrome o Edge. En este proyecto el servidor se ejecuta en **tu propia computadora** (`http://localhost:8501`). No exige conocimientos de HTML o JavaScript para hacer ajustes básicos.

## Instalación y uso en Windows

**Requisitos:** Windows 10/11, Python 3.11 a 3.15 y conexión a Internet la primera vez que se instalan paquetes.

1. Extrae el ZIP en una carpeta privada: por ejemplo `C:\Proyectos\Comparador_PEJENP`.
2. Instala Python desde https://www.python.org/downloads/windows/ (habilita que se pueda ejecutar desde CMD; en versiones con Python Install Manager, `py` sirve).
3. Abre la carpeta extraída y haz doble clic en **`INICIAR_WINDOWS.bat`**.
4. La primera ejecución crea `.venv`, instala las dependencias y abre el navegador en `http://localhost:8501`.
5. En la barra lateral **selecciona tu archivo Excel original** (o una copia autorizada) con el botón de carga. También podrás elegir versiones nuevas que mantengan las mismas columnas.
6. Para cerrar la aplicación presiona `Ctrl+C` en la ventana de CMD abierta.

### Instalación manual si lo prefieres (CMD)

```bat
cd C:\Proyectos\Comparador_PEJENP
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Los comandos de prueba son:

```bat
python -m pip install pytest
python -m pytest -q
```

## Cómo utilizar la aplicación

1. Selecciona especialidad, subespecialidad, instancia, órgano jurisdiccional y bandeja.
2. Marca **dos o más tareas de origen** (por ejemplo, Inadmisibles y Pendientes de calificación).
3. Elige el **mismo motivo de ingreso** a comparar en ambas tareas.
4. Inspecciona los indicadores de actos comunes, actos ausentes en alguna tarea y transiciones diferentes.
5. Consulta la tabla por tarea, y abre el detalle por acto con sus estados/bandejas/tareas destino y `Fila Excel`.
6. Busca pendientes y exporta los resultados a CSV compatible con Excel (separado por punto y coma).

## Alcances funcionales

- La importación se basa en la **hoja `PROCESO ÚNICO`**, encabezados fila 2, registros fila 3 en adelante; valida las posiciones A, D, F, G, I, K, M, O, Q, S, U, W, Y, AA, AC, AE, AG.
- Compara los actos por **mayúsculas/espacios normalizados**. No altera el texto visible original.
- Un valor exacto `PENDIENTE`, una celda vacía y errores definidos de Excel son pendientes. El estado `EN TRAMITE(PENDIENTE)` conserva su significado.
- Los 5 campos usados para completitud son: acto procesal, estado origen, estado destino, bandeja destino, tarea destino.
- La **presencia de información no equivale a corrección**. Los contadores no presuponen que todos esos campos sean obligatorios en cada regla.
- Las diferencias no se consideran defectos funcionales sin validación de PP0067/dueños de proceso.
- No sobrescribe el Excel y no persiste los cambios en los registros: es una herramienta de **solo lectura**.

## Uso con Codex

1. Instala Codex app o la extensión Codex para VS Code. Abre **esta carpeta de proyecto**, no solamente el archivo HTML.
2. Lee primero `AGENTS.md` y `PROMPT_PARA_CODEX.md`.
3. Pide que revise y ejecute las pruebas sin enviar ni publicar tu matriz institucional.
4. Usa Git para guardar versiones del código, pero **nunca subas el Excel ni información institucional a repositorios públicos**. El `.gitignore` excluye `data/*.xlsx`.

### Precaución de privacidad

El ZIP **NO incluye la matriz institucional**; tendrás que cargarla desde la barra lateral de la aplicación. Esto es deliberado para que puedas abrir el código con Codex sin adjuntar inadvertidamente el Excel. Nunca arrastres el archivo institucional a Codex ni le pidas leerlo sin autorización de tu entidad: un agente de codificación puede remitir a sus servicios el contenido que analiza. Usa datos sintéticos o anonimizados cuando pidas cambios de código. El Excel original no se modifica.

## Estructura

```
app.py                  interfaz Streamlit
matrix_core.py          importación y cálculos
requirements.txt        bibliotecas Python
INICIAR_WINDOWS.bat     inicio asistido en Windows
AGENTS.md               reglas y restricciones para Codex
PROMPT_PARA_CODEX.md    instrucciones para trabajar con Codex
data/                   carpeta opcional para pruebas locales (sin el Excel en este ZIP)
tests/                  verificaciones automáticas
.streamlit/config.toml  interfaz y enlace local
```

## Validación de entrega

La lógica de `matrix_core.py` se probó con la matriz de origen del usuario antes de preparar el ZIP. No fue posible iniciar el servidor Streamlit en el entorno de creación por falta de acceso a los paquetes en línea; la primera ejecución de la interfaz se hará en tu Windows.
