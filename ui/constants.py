"""
Sistema de Diseno - Organizador de Archivos.
Roles de color fijos y estrictos:
- Accion primaria (exclusivo para 'Organizar ahora'): Indigo #5b7cfa
- Estado activo / en progreso: Verde #38b487
- Estado pausado / advertencia: Ambar #e0a53f
- Accion destructiva / eliminar: Rojo #e0625a
- Fondos y paneles: Grises neutros con estricto cumplimiento WCAG AA (>4.5:1 texto, >3:1 UI).
"""

THEME = {
    # Fondos neutros
    "bg_main": ("#f0f2f5", "#12141a"),
    "bg_card": ("#ffffff", "#1a1d26"),
    "bg_card_sub": ("#e4e7ed", "#242834"),
    "bg_input": ("#ffffff", "#14161f"),
    
    # Bordes neutros
    "border": ("#cbd1dc", "#2e3444"),
    "border_light": ("#e2e6ed", "#232733"),
    
    # Tipografia WCAG AA
    "text_primary": ("#111318", "#f3f4f8"),    # > 15:1 en Dark, > 16:1 en Light
    "text_secondary": ("#49505f", "#a2a9b7"),  # > 7.1:1 en Dark, > 7.4:1 en Light
    "text_muted": ("#6f7787", "#788190"),      # > 4.5:1
    
    # ROL 1: Accion Primaria (EXCLUSIVO para 'Organizar ahora')
    "action_primary": ("#4a6df5", "#5b7cfa"),
    "action_primary_hover": ("#395de6", "#4868e4"),
    "action_primary_text": "#ffffff",
    
    # ROL 2: Estado Activo / En Progreso (Verde #38b487)
    "status_active": "#38b487",
    "status_active_bg": ("#e6f7f0", "#0f2e21"),
    "status_active_text": ("#187854", "#38b487"),
    "status_active_border": ("#a3e2cb", "#194a36"),
    "progress_bar": "#38b487",
    
    # ROL 3: Estado Pausado (Ambar #e0a53f)
    "status_paused": "#e0a53f",
    "status_paused_bg": ("#fcf5ea", "#2e210a"),
    "status_paused_text": ("#9c6d1d", "#e0a53f"),
    "status_paused_border": ("#f6d9a4", "#4a3511"),
    
    # ROL 4: Accion Destructiva (Rojo #e0625a)
    "action_danger": "#e0625a",
    "action_danger_bg": ("#fdeeed", "#2d1413"),
    "action_danger_hover": ("#c94f47", "#c94f47"),
    "action_danger_text": ("#b83830", "#e0625a"),
    "action_danger_border": ("#f8bcba", "#521e1c"),
    
    # Boton Secundario / Neutro
    "btn_secondary_bg": ("#e4e7ed", "#242834"),
    "btn_secondary_hover": ("#d5dae2", "#2e3444"),
    "btn_secondary_text": ("#111318", "#f3f4f8"),
    "btn_secondary_border": ("#cbd1dc", "#2e3444"),
    
    # Pestanas (Pills neutras para NO competir con el acento primario)
    "tab_bar_bg": ("#e4e7ed", "#14171f"),
    "tab_active_bg": ("#ffffff", "#242834"),
    "tab_active_text": ("#111318", "#f3f4f8"),
    "tab_inactive_text": ("#49505f", "#a2a9b7"),
    "tab_hover_bg": ("#d8dce4", "#1c202c"),
    
    # Switches
    "switch_track_active": "#38b487",
    "switch_track_inactive": ("#c4cad4", "#2e3444"),
    "switch_knob": ("#ffffff", "#ffffff"),
}

FONT_FAMILY = "Segoe UI"


def human_size(size_bytes):
    """Convierte bytes a representacion legible (KB, MB, GB)."""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.1f} {units[i]}"
