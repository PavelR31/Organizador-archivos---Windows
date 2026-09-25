"""
Organizer Core - Motor principal del organizador de archivos.

Maneja: monitoreo de carpeta con watchdog, categorizacion, movimiento de archivos,
historial de operaciones (undo), estadisticas, y configuracion persistente.
"""

import json
import time
import shutil
import threading
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Ruta de configuracion y datos ---
APP_DATA_DIR = Path.home() / ".FileOrganizer"
CONFIG_FILE = APP_DATA_DIR / "config.json"
HISTORY_FILE = APP_DATA_DIR / "history.json"
STATS_FILE = APP_DATA_DIR / "stats.json"

# --- Categorias y Subcarpetas por defecto ---
DEFAULT_CATEGORIES = {
    "Documentos/Word": [".docx", ".doc"],
    "Documentos/PDF": [".pdf"],
    "Documentos/Excel": [".xlsx", ".xls", ".csv"],
    "Documentos/PowerPoint": [".pptx", ".ppt"],
    "Documentos/Texto": [".txt", ".odt", ".rtf"],
    "Imagenes/Sin Fondo": [".png"],
    "Imagenes/Fotos": [".jpg", ".jpeg", ".webp", ".bmp", ".tiff"],
    "Imagenes/Iconos y Vectores": [".svg", ".ico"],
    "Imagenes/Animaciones": [".gif"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv", ".webm"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Software": [".exe", ".msi", ".dmg", ".deb", ".rpm", ".appimage"],
    "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Codigo": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".ts", ".json", ".xml", ".yaml", ".yml"],
    "Otros": []
}


def ensure_app_data():
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    ensure_app_data()
    default_cfg = {
        "watch_dir": str(Path.home() / "Downloads"),
        "categories": DEFAULT_CATEGORIES,
        "autostart": False,
        "theme": "dark",
        "notifications": True,
        "organize_on_start": True
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            # Migrar a subcarpetas si se detecta esquema plano antiguo
            cats = config.get("categories", {})
            if "Imagenes" in cats and "Imagenes/Sin Fondo" not in cats:
                config["categories"] = DEFAULT_CATEGORIES
            for k, v in default_cfg.items():
                if k not in config:
                    config[k] = v
            save_config(config)
            return config
        except (json.JSONDecodeError, KeyError):
            pass
    save_config(default_cfg)
    return default_cfg


def save_config(config):
    ensure_app_data()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_history():
    ensure_app_data()
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass
    return []


def save_history(history):
    ensure_app_data()
    history = history[-500:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_stats():
    ensure_app_data()
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass
    return {"total_moved": 0, "by_category": {}, "by_date": {}}


def save_stats(stats):
    ensure_app_data()
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def undo_move(entry):
    src = Path(entry["dest"])
    dst = Path(entry["source"])
    if not src.exists():
        return False, f"El archivo ya no existe en: {src}"
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return True, f"Restaurado: {dst.name}"
    except Exception as e:
        return False, f"Error al restaurar: {e}"


def organize_existing_files(watch_dir, categories, on_progress=None):
    watch_path = Path(watch_dir)
    if not watch_path.exists():
        return []
    history_entries = []
    try:
        files = [
            f for f in watch_path.iterdir()
            if f.is_file() and f.suffix.lower() not in ('.tmp', '.crdownload', '.part', '.download')
        ]
        total = len(files)
        for i, archivo in enumerate(files, 1):
            if on_progress:
                try:
                    on_progress(i, total, archivo.name)
                except Exception:
                    pass
            extension = archivo.suffix.lower()
            categoria = _get_category(extension, categories)
            entry = _move_file(archivo, categoria, watch_path)
            if entry:
                history_entries.append(entry)
    except Exception:
        pass
    return history_entries


def _get_category(extension, categories):
    for cat, exts in categories.items():
        if extension in exts:
            return cat
    return "Otros"


def _move_file(archivo, categoria, watch_dir):
    destino = watch_dir / categoria
    destino.mkdir(parents=True, exist_ok=True)
    destino_final = destino / archivo.name
    contador = 1
    while destino_final.exists():
        nombre_base = f"{archivo.stem}_{contador}"
        destino_final = destino / f"{nombre_base}{archivo.suffix}"
        contador += 1
    try:
        shutil.move(str(archivo), str(destino_final))
        entry = {
            "source": str(archivo),
            "dest": str(destino_final),
            "category": categoria,
            "filename": archivo.name,
            "timestamp": datetime.now().isoformat(),
            "size": destino_final.stat().st_size if destino_final.exists() else 0
        }
        return entry
    except Exception:
        return None


class FileOrganizerHandler(FileSystemEventHandler):
    def __init__(self, categories, watch_dir, on_file_moved=None, on_log=None):
        super().__init__()
        self.categories = categories
        self.watch_dir = Path(watch_dir)
        self.on_file_moved = on_file_moved
        self.on_log = on_log

    def on_created(self, event):
        if event.is_directory:
            return
        archivo = Path(event.src_path)
        if archivo.parent != self.watch_dir:
            return
        if archivo.suffix.lower() in ('.tmp', '.crdownload', '.part', '.download'):
            return
        self._log(f"[INFO] Archivo detectado: {archivo.name}")
        threading.Thread(target=self._wait_and_process, args=(archivo,), daemon=True).start()

    def _wait_and_process(self, archivo):
        time.sleep(2)
        if not archivo.exists():
            return
        try:
            size1 = archivo.stat().st_size
            time.sleep(1)
            if not archivo.exists():
                return
            size2 = archivo.stat().st_size
            if size1 != size2:
                time.sleep(3)
                if not archivo.exists():
                    return
        except OSError:
            return
        extension = archivo.suffix.lower()
        categoria = _get_category(extension, self.categories)
        entry = _move_file(archivo, categoria, self.watch_dir)
        if entry:
            self._log(f"[INFO] Movido: {entry['filename']} -> {categoria}/")
            if self.on_file_moved:
                self.on_file_moved(entry)
        else:
            self._log(f"[ERROR] Error al mover: {archivo.name}")

    def _log(self, message):
        if self.on_log:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.on_log(f"[{timestamp}] {message}")


class FileOrganizerEngine:
    def __init__(self):
        self.config = load_config()
        self.history = load_history()
        self.stats = load_stats()
        self.observer = None
        self.is_running = False
        self._on_file_moved = None
        self._on_log = None
        self._on_status_change = None
        self._on_progress = None

    def set_callbacks(self, on_file_moved=None, on_log=None, on_status_change=None, on_progress=None):
        self._on_file_moved = on_file_moved
        self._on_log = on_log
        self._on_status_change = on_status_change
        self._on_progress = on_progress

    def log(self, message, level="INFO"):
        if self._on_log:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._on_log(f"[{timestamp}] [{level}] {message}")

    def start(self, skip_retrospective=False):
        if self.is_running:
            return
        watch_dir = self.config.get("watch_dir", "")
        if not Path(watch_dir).exists():
            self.log(f"La carpeta configurada no existe: {watch_dir}", level="ERROR")
            return
        
        # Organizacion retrospectiva si esta habilitada
        if not skip_retrospective and self.config.get("organize_on_start", True):
            self._run_retrospective(watch_dir)

        # Monitoreo en tiempo real
        handler = FileOrganizerHandler(
            categories=self.config["categories"],
            watch_dir=watch_dir,
            on_file_moved=self._handle_file_moved,
            on_log=self._on_log
        )
        self.observer = Observer()
        self.observer.schedule(handler, watch_dir, recursive=False)
        self.observer.start()
        self.is_running = True
        self.log(f"Monitoreo activo en: {watch_dir}", level="INFO")
        if self._on_status_change:
            self._on_status_change(True)

    def _run_retrospective(self, watch_dir):
        """Organiza los archivos existentes en la carpeta antes de iniciar el monitoreo."""
        watch_path = Path(watch_dir)
        try:
            pending_files = [f for f in watch_path.iterdir() if f.is_file()]
        except Exception as e:
            self.log(f"No se pudo acceder a {watch_dir}: {e}", level="ERROR")
            return

        if not pending_files:
            self.log(f"No hay archivos pendientes en {watch_dir}", level="INFO")
            return

        self.log(f"Organizacion retrospectiva: {len(pending_files)} archivo(s) detectado(s)", level="INFO")
        entries = organize_existing_files(watch_dir, self.config["categories"], on_progress=self._on_progress)
        for entry in entries:
            self._handle_file_moved(entry)
            self.log(f"Movido: {entry['filename']} -> {entry['category']}/", level="INFO")
        self.log(f"Retrospectiva completada: {len(entries)} archivo(s) procesado(s)", level="INFO")

    def stop(self):
        if not self.is_running:
            return
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5)
            self.observer = None
        self.is_running = False
        self.log("Monitoreo detenido", level="INFO")
        if self._on_status_change:
            self._on_status_change(False)

    def set_watch_dir(self, new_dir):
        """Cambia dinamicamente la carpeta monitoreada."""
        new_path = Path(new_dir)
        if not new_path.exists():
            return False, f"La carpeta no existe: {new_dir}"
        
        was_running = self.is_running
        if was_running:
            self.stop()
        
        self.update_config(watch_dir=str(new_path))
        self.log(f"Carpeta de monitoreo actualizada a: {new_path}", level="INFO")
        
        if was_running:
            self.start(skip_retrospective=False)
        return True, "Carpeta actualizada correctamente"

    def _handle_file_moved(self, entry):
        self.history.append(entry)
        save_history(self.history)
        self.stats["total_moved"] = self.stats.get("total_moved", 0) + 1
        cat = entry["category"]
        self.stats.setdefault("by_category", {})
        self.stats["by_category"][cat] = self.stats["by_category"].get(cat, 0) + 1
        date_key = datetime.now().strftime("%Y-%m-%d")
        self.stats.setdefault("by_date", {})
        self.stats["by_date"][date_key] = self.stats["by_date"].get(date_key, 0) + 1
        save_stats(self.stats)
        if self._on_file_moved:
            self._on_file_moved(entry)

    def undo_last(self):
        if not self.history:
            return False, "No hay movimientos para deshacer"
        entry = self.history.pop()
        success, msg = undo_move(entry)
        save_history(self.history)
        if success:
            self.stats["total_moved"] = max(0, self.stats.get("total_moved", 0) - 1)
            cat = entry["category"]
            if cat in self.stats.get("by_category", {}):
                self.stats["by_category"][cat] = max(0, self.stats["by_category"][cat] - 1)
            save_stats(self.stats)
        return success, msg

    def undo_entry(self, index):
        if index < 0 or index >= len(self.history):
            return False, "Indice fuera de rango"
        entry = self.history.pop(index)
        success, msg = undo_move(entry)
        save_history(self.history)
        return success, msg

    def organize_now(self, on_progress=None):
        prog = on_progress or self._on_progress
        entries = organize_existing_files(
            self.config["watch_dir"],
            self.config["categories"],
            on_progress=prog
        )
        for entry in entries:
            self._handle_file_moved(entry)
            self.log(f"Movido: {entry['filename']} -> {entry['category']}/", level="INFO")
        return len(entries)

    def update_config(self, **kwargs):
        self.config.update(kwargs)
        save_config(self.config)

    def get_watch_dir_info(self):
        watch_dir = Path(self.config.get("watch_dir", ""))
        if not watch_dir.exists():
            return {"exists": False, "file_count": 0, "total_size": 0, "path": str(watch_dir)}
        files = [f for f in watch_dir.iterdir() if f.is_file()]
        total_size = sum(f.stat().st_size for f in files)
        return {
            "exists": True,
            "file_count": len(files),
            "total_size": total_size,
            "path": str(watch_dir)
        }
