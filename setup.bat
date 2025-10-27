@echo off
REM Script de Configuracion Inicial - CarroIoT Backend API
REM Para Windows Server en EC2

echo ============================================================
echo    CarroIoT Backend API - Configuracion Inicial
echo ============================================================
echo.

REM Verificar Python
echo [1/5] Verificando Python...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    echo Por favor instala Python 3.11 desde https://www.python.org/downloads/
    echo IMPORTANTE: Marca la casilla 'Add Python to PATH' durante la instalacion
    pause
    exit /b 1
)

python --version
echo OK - Python encontrado
echo.

REM Crear entorno virtual
echo [2/5] Creando entorno virtual...
if exist "venv" (
    echo El entorno virtual ya existe
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo OK - Entorno virtual creado
)
echo.

REM Activar entorno virtual
echo [3/5] Activando entorno virtual...
call venv\Scripts\activate.bat
echo OK - Entorno virtual activado
echo.

REM Actualizar pip
echo [4/5] Actualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar dependencias
echo [5/5] Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo.

echo ============================================================
echo  Configuracion completada exitosamente!
echo ============================================================
echo.
echo Proximos pasos:
echo.
echo 1. Verifica que el archivo .env tenga las credenciales correctas
echo 2. Ejecuta: start.bat para iniciar el servidor
echo 3. Prueba en navegador: http://localhost:5500/
echo.
echo ============================================================
pause
