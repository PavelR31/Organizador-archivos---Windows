"""
Autostart Manager - Maneja el inicio automatico con Windows para Organizador de Archivos.
Usa el registro de Windows (HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run).
"""

import sys
import os

REG_KEY_NAME = "OrganizadorArchivos"
OLD_KEY_NAME = "FileOrganizer"

def _get_startup_key():
    """Obtiene la clave del registro para startup."""
    try:
        import winreg
        return winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_ALL_ACCESS
        )
    except Exception:
        return None

def is_autostart_enabled():
    """Verifica si la app esta en el startup de Windows."""
    try:
        import winreg
        key = _get_startup_key()
        if key is None:
            return False
        enabled = False
        try:
            winreg.QueryValueEx(key, REG_KEY_NAME)
            enabled = True
        except FileNotFoundError:
            try:
                winreg.QueryValueEx(key, OLD_KEY_NAME)
                enabled = True
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return enabled
    except Exception:
        return False

def enable_autostart():
    """Agrega la app al startup de Windows."""
    try:
        import winreg
        key = _get_startup_key()
        if key is None:
            return False
        # Limpiar clave antigua si existe
        try:
            winreg.DeleteValue(key, OLD_KEY_NAME)
        except FileNotFoundError:
            pass

        if getattr(sys, 'frozen', False):
            app_path = f'"{sys.executable}" --minimized'
        else:
            app_path = f'"{sys.executable}" "{os.path.abspath(os.path.join(os.path.dirname(__file__), "app.py"))}" --minimized'
        winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_SZ, app_path)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def disable_autostart():
    """Remueve la app del startup de Windows."""
    try:
        import winreg
        key = _get_startup_key()
        if key is None:
            return False
        for k in (REG_KEY_NAME, OLD_KEY_NAME):
            try:
                winreg.DeleteValue(key, k)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def set_autostart(enabled):
    """Activa o desactiva el autostart."""
    if enabled:
        return enable_autostart()
    else:
        return disable_autostart()
