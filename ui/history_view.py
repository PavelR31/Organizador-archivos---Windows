"""
Vista de Historial y Actividad - Organizador de Archivos.
"""

import customtkinter as ctk
from .constants import THEME, FONT_FAMILY, human_size


def build_history_tab(parent, app):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=20, pady=15)

    card = ctk.CTkFrame(frame, fg_color=THEME["bg_card"], corner_radius=8, border_width=1, border_color=THEME["border"])
    card.pack(fill="both", expand=True)

    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=16, pady=14)

    header_row = ctk.CTkFrame(inner, fg_color="transparent")
    header_row.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(
        header_row,
        text="Registro de Actividad Reciente",
        font=(FONT_FAMILY, 13, "bold"),
        text_color=THEME["text_primary"]
    ).pack(side="left")

    ctk.CTkButton(
        header_row,
        text="Deshacer ultimo",
        font=(FONT_FAMILY, 11),
        height=28,
        fg_color=THEME["btn_secondary_bg"],
        hover_color=THEME["btn_secondary_hover"],
        text_color=THEME["btn_secondary_text"],
        border_width=1,
        border_color=THEME["border"],
        corner_radius=6,
        command=app.undo_last_action
    ).pack(side="right")

    # Contenedor con scroll para lista de movimientos
    app.history_scroll = ctk.CTkScrollableFrame(
        inner,
        fg_color=THEME["bg_input"],
        border_width=1,
        border_color=THEME["border"],
        corner_radius=6
    )
    app.history_scroll.pack(fill="both", expand=True, pady=(4, 0))

    app.refresh_history_list()
    return frame
