"""
Vista de Configuracion General - Organizador de Archivos.
Jerarquia de color estricta:
- 'Organizar ahora' es la UNICA accion primaria a pleno color (Indigo #5b7cfa).
- Visibilidad de proceso en tiempo real (barra de progreso + contador X/Total).
- Opciones y botones secundarios en grises neutros sin competir con la accion primaria.
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from .constants import THEME, FONT_FAMILY


def build_general_tab(parent, app):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=20, pady=15)

    # --- Panel 1: Carpeta Monitoreada & Accion Primaria ---
    folder_card = ctk.CTkFrame(frame, fg_color=THEME["bg_card"], corner_radius=8, border_width=1, border_color=THEME["border"])
    folder_card.pack(fill="x", pady=(0, 14))

    folder_inner = ctk.CTkFrame(folder_card, fg_color="transparent")
    folder_inner.pack(fill="x", padx=16, pady=14)

    ctk.CTkLabel(
        folder_inner,
        text="Carpeta Monitoreada",
        font=(FONT_FAMILY, 13, "bold"),
        text_color=THEME["text_primary"]
    ).pack(anchor="w", pady=(0, 4))

    ctk.CTkLabel(
        folder_inner,
        text="Los archivos nuevos o existentes en este directorio seran organizados en sus subcarpetas correspondientes.",
        font=(FONT_FAMILY, 11),
        text_color=THEME["text_secondary"]
    ).pack(anchor="w", pady=(0, 10))

    # Fila de seleccion de carpeta
    input_row = ctk.CTkFrame(folder_inner, fg_color="transparent")
    input_row.pack(fill="x", pady=(0, 10))

    app.folder_entry = ctk.CTkEntry(
        input_row,
        height=34,
        font=(FONT_FAMILY, 11),
        fg_color=THEME["bg_input"],
        text_color=THEME["text_primary"],
        border_color=THEME["border"],
        border_width=1,
        corner_radius=6
    )
    app.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
    app.folder_entry.insert(0, app.engine.config.get("watch_dir", ""))

    ctk.CTkButton(
        input_row,
        text="Examinar...",
        font=(FONT_FAMILY, 11),
        width=90,
        height=34,
        fg_color=THEME["btn_secondary_bg"],
        hover_color=THEME["btn_secondary_hover"],
        text_color=THEME["btn_secondary_text"],
        border_width=1,
        border_color=THEME["btn_secondary_border"],
        corner_radius=6,
        command=app.browse_folder
    ).pack(side="left", padx=(0, 6))

    ctk.CTkButton(
        input_row,
        text="Abrir",
        font=(FONT_FAMILY, 11),
        width=70,
        height=34,
        fg_color=THEME["btn_secondary_bg"],
        hover_color=THEME["btn_secondary_hover"],
        text_color=THEME["btn_secondary_text"],
        border_width=1,
        border_color=THEME["btn_secondary_border"],
        corner_radius=6,
        command=app.open_watch_folder
    ).pack(side="left")

    # Fila de accion primaria: 'Organizar ahora' es el unico boton con acento indigo a pleno color
    action_row = ctk.CTkFrame(folder_inner, fg_color="transparent")
    action_row.pack(fill="x", pady=(2, 0))

    app.btn_organize_now = ctk.CTkButton(
        action_row,
        text="Organizar ahora",
        font=(FONT_FAMILY, 12, "bold"),
        height=36,
        width=140,
        fg_color=THEME["action_primary"],
        hover_color=THEME["action_primary_hover"],
        text_color=THEME["action_primary_text"],
        corner_radius=6,
        command=app.organize_now
    )
    app.btn_organize_now.pack(side="left")

    # Contenedor de Visibilidad de Proceso en Tiempo Real
    app.process_frame = ctk.CTkFrame(folder_inner, fg_color="transparent")
    app.process_frame.pack(fill="x", pady=(10, 0))

    app.process_progress_bar = ctk.CTkProgressBar(
        app.process_frame,
        height=6,
        progress_color=THEME["progress_bar"],
        fg_color=THEME["bg_card_sub"],
        corner_radius=3
    )
    app.process_progress_bar.set(0)

    app.process_status_label = ctk.CTkLabel(
        app.process_frame,
        text="",
        font=(FONT_FAMILY, 11),
        text_color=THEME["text_secondary"],
        anchor="w"
    )

    # --- Panel 2: Opciones del Sistema ---
    opts_card = ctk.CTkFrame(frame, fg_color=THEME["bg_card"], corner_radius=8, border_width=1, border_color=THEME["border"])
    opts_card.pack(fill="x")

    opts_inner = ctk.CTkFrame(opts_card, fg_color="transparent")
    opts_inner.pack(fill="x", padx=16, pady=14)

    ctk.CTkLabel(
        opts_inner,
        text="Opciones del Sistema",
        font=(FONT_FAMILY, 13, "bold"),
        text_color=THEME["text_primary"]
    ).pack(anchor="w", pady=(0, 10))

    # Switch 1: Iniciar con Windows
    sw1_row = ctk.CTkFrame(opts_inner, fg_color="transparent")
    sw1_row.pack(fill="x", pady=4)
    app.autostart_var = ctk.BooleanVar(value=app.engine.config.get("autostart", False))
    ctk.CTkSwitch(
        sw1_row,
        text="Iniciar en segundo plano al arrancar Windows",
        font=(FONT_FAMILY, 11),
        text_color=THEME["text_primary"],
        variable=app.autostart_var,
        onvalue=True,
        offvalue=False,
        progress_color=THEME["switch_track_active"],
        button_color=THEME["switch_knob"],
        button_hover_color=THEME["switch_knob"],
        command=app.toggle_autostart
    ).pack(side="left")

    # Switch 2: Organizar al iniciar
    sw2_row = ctk.CTkFrame(opts_inner, fg_color="transparent")
    sw2_row.pack(fill="x", pady=4)
    app.retro_var = ctk.BooleanVar(value=app.engine.config.get("organize_on_start", True))
    ctk.CTkSwitch(
        sw2_row,
        text="Organizar archivos existentes al iniciar monitoreo",
        font=(FONT_FAMILY, 11),
        text_color=THEME["text_primary"],
        variable=app.retro_var,
        onvalue=True,
        offvalue=False,
        progress_color=THEME["switch_track_active"],
        button_color=THEME["switch_knob"],
        button_hover_color=THEME["switch_knob"],
        command=app.save_general_preferences
    ).pack(side="left")

    # Switch 3: Notificaciones
    sw3_row = ctk.CTkFrame(opts_inner, fg_color="transparent")
    sw3_row.pack(fill="x", pady=4)
    app.notif_var = ctk.BooleanVar(value=app.engine.config.get("notifications", True))
    ctk.CTkSwitch(
        sw3_row,
        text="Mostrar notificaciones del sistema al clasificar archivos",
        font=(FONT_FAMILY, 11),
        text_color=THEME["text_primary"],
        variable=app.notif_var,
        onvalue=True,
        offvalue=False,
        progress_color=THEME["switch_track_active"],
        button_color=THEME["switch_knob"],
        button_hover_color=THEME["switch_knob"],
        command=app.save_general_preferences
    ).pack(side="left")

    # Switch 4: Modo Oscuro
    sw4_row = ctk.CTkFrame(opts_inner, fg_color="transparent")
    sw4_row.pack(fill="x", pady=4)
    current_theme = app.engine.config.get("theme", "dark")
    app.dark_mode_var = ctk.BooleanVar(value=(current_theme == "dark"))
    ctk.CTkSwitch(
        sw4_row,
        text="Modo Oscuro (Dark Theme)",
        font=(FONT_FAMILY, 11),
        text_color=THEME["text_primary"],
        variable=app.dark_mode_var,
        onvalue=True,
        offvalue=False,
        progress_color=THEME["switch_track_active"],
        button_color=THEME["switch_knob"],
        button_hover_color=THEME["switch_knob"],
        command=app.toggle_dark_mode
    ).pack(side="left")

    return frame
