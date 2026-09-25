@echo off
echo ============================================
echo   Organizador de Archivos - Script de Build
echo ============================================
echo.

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

REM Construir ejecutable
echo.
echo Construyendo ejecutable con icono y soporte para bandeja...
pyinstaller --noconfirm --onefile --windowed ^
    --name "OrganizadorDeArchivos" ^
    --icon "assets\icon.ico" ^
    --add-data "assets;assets" ^
    --hidden-import "plyer.platforms.win.notification" ^
    --hidden-import "customtkinter" ^
    --hidden-import "pystray" ^
    --hidden-import "PIL" ^
    --collect-all "customtkinter" ^
    app.py

echo.
echo ============================================
echo   Build completado exitosamente!
echo   Ejecutable en: dist\OrganizadorDeArchivos.exe
echo ============================================
pause
