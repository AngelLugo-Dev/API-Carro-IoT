@echo off
REM Script de Inicio Rapido - CarroIoT Backend API
REM Para Windows Server en EC2

echo ============================================================
echo        CarroIoT Backend API - Script de Inicio
echo ============================================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "src\app.py" (
    echo ERROR: No se encontro src\app.py
    echo Este script debe ejecutarse desde la carpeta backend-api
    pause
    exit /b 1
)

REM Activar virtual environment
echo [1/3] Activando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo OK - Entorno virtual activado
) else (
    echo ERROR: No se encontro el entorno virtual
    echo Ejecuta primero: python -m venv venv
    pause
    exit /b 1
)

echo.
echo [2/3] Verificando dependencias...
pip list | findstr Flask > nul
if %errorlevel% neq 0 (
    echo ERROR: Flask no esta instalado
    echo Ejecuta: pip install -r requirements.txt
    pause
    exit /b 1
)

echo OK - Dependencias verificadas
echo.

REM Verificar archivo .env
if not exist ".env" (
    echo ADVERTENCIA: No se encontro archivo .env
    echo Asegurate de configurar las variables de entorno
    echo Puedes copiar .env.example a .env y editar las credenciales
    timeout /t 3
)

echo [3/3] Iniciando servidor...
echo.
echo ============================================================
echo  Backend corriendo en: http://0.0.0.0:5500
echo  Presiona Ctrl+C para detener el servidor
echo ============================================================
echo.

cd src
python app.py

REM Si el servidor se detuvo
echo.
echo ============================================================
echo  Servidor detenido
echo ============================================================
pause
