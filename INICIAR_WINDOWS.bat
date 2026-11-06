@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno virtual de Python...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo ERROR: Instala Python 3.11 o superior y vuelve a ejecutar.
    pause
    exit /b 1
  )
)
echo Instalando o verificando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo ERROR: No se pudieron instalar las dependencias. Revisa tu conexion a Internet.
  pause
  exit /b 1
)
echo Abriendo Comparador PEJENP en http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run app.py
pause
