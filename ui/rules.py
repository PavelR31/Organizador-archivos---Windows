"""
Vista de Reglas y Categorias - Organizador de Archivos.
Estricto cumplimiento de jerarquia:
- Botones de configuracion usan tonos neutros elevados.
- Solo la accion destructiva ('Eliminar') utiliza el color rojo #e0625a.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from .constants import THEME, FONT_FAMILY
from organizer_core import DEFAULT_CATEGORIES


def build_rules_tab(parent, app):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=20, pady=15)

    card = ctk.CTkFrame(frame, fg_color=THEME["bg_card"], corner_radius=8, border_width=1, border_color=THEME["border"])
    card.pack(fill="both", expand=True)

    inner = ctk.CTkFrame(card, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=16, pady=14)

    ctk.CTkLabel(
        inner,
        text="Reglas de Clasificacion y Subcarpetas",
        font=(FONT_FAMILY, 13, "bold"),
        text_color=THEME["text_primary"]
    ).pack(anchor="w", pady=(0, 4))

    ctk.CTkLabel(
        inner,
        text="Define que extensiones corresponden a cada destino (ej: 'Documentos/Word' o 'Imagenes/Sin Fondo').",
        font=(FONT_FAMILY, 11),
        text_color=THEME["text_secondary"]
    ).pack(anchor="w", pady=(0, 10))

    # Selector de categoria existente
    sel_row = ctk.CTkFrame(inner, fg_color="transparent")
    sel_row.pack(fill="x", pady=(0, 8))

    ctk.CTkLabel(
        sel_row,
        text="Destino:",
        font=(FONT_FAMILY, 11, "bold"),
        text_color=THEME["text_primary"],
        width=70
    ).pack(side="left")

    categories = list(app.engine.config.get("categories", DEFAULT_CATEGORIES).keys())
    app.rule_cat_var = ctk.StringVar(value=categories[0] if categories else "Documentos/Word")
    app.rule_cat_menu = ctk.CTkOptionMenu(
        sel_row,
        variable=app.rule_cat_var,
        values=categories,
        font=(FONT_FAMILY, 11),
        fg_color=THEME["btn_secondary_bg"],
        button_color=THEME["border"],
        text_color=THEME["btn_secondary_text"],
        dropdown_fg_color=THEME["bg_card"],
        dropdown_text_color=THEME["text_primary"],
        dropdown_hover_color=THEME["btn_secondary_bg"],
        corner_radius=6,
        command=lambda _: app.load_category_extensions()
    )
    app.rule_cat_menu.pack(side="left", fill="x", expand=True, padx=(0, 8))

    # Boton de accion destructiva exclusiva: Rojo #e0625a
    ctk.CTkButton(
        sel_row,
        text="Eliminar",
        font=(FONT_FAMILY, 10, "bold"),
        width=70,
        height=28,
        fg_color=THEME["action_danger_bg"],
        hover_color=THEME["action_danger_hover"],
        text_color=THEME["action_danger_text"],
        border_width=1,
        border_color=THEME["action_danger_border"],
        corner_radius=6,
        command=app.delete_current_category
    ).pack(side="right")

    # Editor de extensiones
    ctk.CTkLabel(
        inner,
        text="Extensiones asignadas a este destino (separadas por coma):",
        font=(FONT_FAMILY, 11),
        text_color=THEME["text_secondary"]
    ).pack(anchor="w", pady=(6, 4))

    app.rule_ext_entry = ctk.CTkTextbox(
        inner,
        height=80,
        font=(FONT_FAMILY, 11),
        fg_color=THEME["bg_input"],
        text_color=THEME["text_primary"],
        border_color=THEME["border"],
        border_width=1,
        corner_radius=6
    )
    app.rule_ext_entry.pack(fill="x", pady=(0, 10))

    # Fila para agregar nueva subcarpeta
    add_row = ctk.CTkFrame(inner, fg_color="transparent")
    add_row.pack(fill="x", pady=(0, 12))

    app.new_cat_entry = ctk.CTkEntry(
        add_row,
        placeholder_text="Nueva subcarpeta (ej: Documentos/Facturas)...",
        font=(FONT_FAMILY, 11),
        height=32,
        fg_color=THEME["bg_input"],
        text_color=THEME["text_primary"],
        border_color=THEME["border"],
        border_width=1,
        corner_radius=6
    )
    app.new_cat_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

    ctk.CTkButton(
        add_row,
        text="+ Crear subcarpeta",
        font=(FONT_FAMILY, 11),
        width=135,
        height=32,
        fg_color=THEME["btn_secondary_bg"],
        hover_color=THEME["btn_secondary_hover"],
        text_color=THEME["btn_secondary_text"],
        border_width=1,
        border_color=THEME["btn_secondary_border"],
        corner_radius=6,
        command=app.add_new_category
    ).pack(side="right")

    # Botones de accion: usan estilo neutro para no competir con 'Organizar ahora'
    btn_row = ctk.CTkFrame(inner, fg_color="transparent")
    btn_row.pack(fill="x")

    ctk.CTkButton(
        btn_row,
        text="Guardar cambios",
        font=(FONT_FAMILY, 11, "bold"),
        height=32,
        fg_color=THEME["btn_secondary_bg"],
        hover_color=THEME["btn_secondary_hover"],
        text_color=THEME["btn_secondary_text"],
        border_width=1,
        border_color=THEME["border"],
        corner_radius=6,
        command=app.save_current_category
    ).pack(side="left", padx=(0, 8))

    ctk.CTkButton(
        btn_row,
        text="Restaurar por defecto",
        font=(FONT_FAMILY, 11),
        height=32,
        fg_color=THEME["bg_card"],
        hover_color=THEME["btn_secondary_hover"],
        text_color=THEME["text_secondary"],
        border_width=1,
        border_color=THEME["border"],
        corner_radius=6,
        command=app.reset_categories
    ).pack(side="left")

    app.load_category_extensions()
    return frame
