@echo off
echo ========================================
echo Sistema de Historia Clinica Ginecologica
echo ========================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar si existe el entorno virtual
if not exist "venv\" (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias si es necesario
echo Verificando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

REM Ejecutar la aplicacion
echo.
echo Iniciando aplicacion...
echo Abre tu navegador en: http://127.0.0.1:5001/login
echo Presiona Ctrl+C para detener la aplicacion
echo.
python wsgi.py

pause