# Organizador de archivos - Windows Desktop App

Organizador automatico de archivos para Windows con interfaz grafica moderna.

## Que hace?
Monitorea tu carpeta de Descargas (u otra carpeta) y organiza automaticamente los archivos nuevos en subcarpetas por tipo:
- Imagenes (.jpg, .png, .gif...)
- Documentos (.pdf, .docx, .xlsx...)
- Videos (.mp4, .mkv, .avi...)
- Audio (.mp3, .wav, .flac...)
- Software (.exe, .msi...)
- Comprimidos (.zip, .rar, .7z...)
- Codigo (.py, .js, .html...)
- Otros

## Funcionalidades
- Dashboard con estadisticas en tiempo real
- Historial de movimientos con opcion de deshacer
- Categorias editables (agregar/quitar extensiones)
- Tema oscuro/claro
- Inicio automatico con Windows
- Notificaciones nativas de Windows
- Organizar archivos existentes con un clic
- Log de actividad en tiempo real

## Requisitos
- Python 3.10+ (probado con 3.14)
- Windows 10/11

## Instalacion
```bash
# Clonar o copiar el proyecto
cd FileOrganizer

# Crear entorno virtual e instalar dependencias
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# Ejecutar la app
venv\Scripts\python app.py
```

## Crear ejecutable (.exe)
```bash
# Ejecutar el script de build
build.bat

# O manualmente:
venv\Scripts\pyinstaller --noconfirm --onefile --windowed --name FileOrganizer --collect-all customtkinter app.py
```
El ejecutable se genera en `dist\FileOrganizer.exe`

## Estructura del proyecto
```
FileOrganizer/
  app.py              - Interfaz grafica (CustomTkinter)
  organizer_core.py   - Motor de organizacion y monitoreo
  autostart.py        - Manejo de inicio automatico con Windows
  requirements.txt    - Dependencias de Python
  build.bat           - Script para crear el .exe
  assets/             - Iconos y recursos
```

## Datos de la app
La configuracion se guarda en: `%USERPROFILE%\.FileOrganizer\`
