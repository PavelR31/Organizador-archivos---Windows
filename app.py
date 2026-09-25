"""
Organizador de Archivos - Utilidad en segundo plano con bandeja de sistema.
Jerarquia funcional estricta:
- Accion primaria (Indigo #5b7cfa): Exclusivo para 'Organizar ahora'.
- Estado activo / en progreso (Verde #38b487): Indicador ACTIVO, progreso y contador.
- Estado pausado (Ambar #e0a53f): Indicador PAUSADO.
- Accion destructiva (Rojo #e0625a): Eliminar / Salir.
- Fondos y paneles: Grises neutros certificados WCAG AA.
"""

import os
import sys
import threading
from pathlib import Path
from datetime import datetime
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import pystray
from pystray import MenuItem as item

# Asegurar path local
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from organizer_core import FileOrganizerEngine, DEFAULT_CATEGORIES
from autostart import set_autostart, is_autostart_enabled
from ui import (
    THEME,
    FONT_FAMILY,
    human_size,
    build_general_tab,
    build_rules_tab,
    build_history_tab
)


class FileOrganizerApp(ctk.CTk):
    def __init__(self, start_minimized=False):
        super().__init__()
        self.title("Organizador de Archivos")
        self.geometry("640x560")
        self.minsize(600, 500)
        self.configure(fg_color=THEME["bg_main"])

        # Icono de ventana
        self.icon_path = BASE_DIR / "assets" / "icon.ico"
        self.png_icon_path = BASE_DIR / "assets" / "icon.png"
        if self.icon_path.exists():
            try:
                self.iconbitmap(str(self.icon_path))
            except Exception:
                pass

        # Inicializar motor con callbacks
        self.engine = FileOrganizerEngine()
        self.engine.set_callbacks(
            on_file_moved=self._on_file_moved,
            on_log=self._on_log,
            on_status_change=self._on_status_change,
            on_progress=self._on_engine_progress
        )

        # Aplicar tema guardado
        theme = self.engine.config.get("theme", "dark")
        ctk.set_appearance_mode(theme)

        # Variables de estado
        self.current_tab = "General"
        self.tab_frames = {}
        self.tab_buttons = {}
        self._progress_reset_timer = None

        # Construir UI
        self._build_header()
        self._build_tab_bar()
        self._build_content_area()
        self._build_footer()

        # Configurar intercepcion de cerrado de ventana (ocultar a la bandeja)
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        # Iniciar icono de bandeja del sistema
        self.tray_icon = None
        self._init_tray_icon()

        # Iniciar motor en segundo plano tras arrancar el bucle principal
        self.after(100, self._start_engine_background)

        # Si se solicita minimizado, ocultar la ventana inmediatamente
        if start_minimized:
            self.withdraw()

    def _start_engine_background(self):
        threading.Thread(target=self.engine.start, daemon=True).start()

    def safe_after(self, fn):
        """Ejecuta una funcion en el hilo principal de Tkinter de forma segura."""
        try:
            if self.winfo_exists():
                self.after(0, fn)
        except Exception:
            pass

    # --- BANDEJA DEL SISTEMA (PYSTRAY) ---

    def _init_tray_icon(self):
        try:
            if self.png_icon_path.exists():
                tray_image = Image.open(str(self.png_icon_path))
            else:
                tray_image = Image.new("RGBA", (64, 64), (79, 112, 245, 255))
        except Exception:
            tray_image = Image.new("RGBA", (64, 64), (79, 112, 245, 255))

        menu = pystray.Menu(
            item("Estado: Activo", self._tray_toggle_status, checked=lambda _: self.engine.is_running),
            item("Organizar ahora", lambda _: self.organize_now()),
            item("Abrir carpeta", lambda _: self.open_watch_folder()),
            pystray.Menu.SEPARATOR,
            item("Preferencias...", lambda _: self.safe_after(self.show_window), default=True),
            item("Salir de Organizador de Archivos", lambda _: self.safe_after(self.quit_app))
        )

        self.tray_icon = pystray.Icon("OrganizadorArchivos", tray_image, "Organizador de Archivos", menu=menu)
        self.tray_icon.run_detached()

    def _tray_toggle_status(self, icon, item):
        self.safe_after(self.toggle_monitoring)

    def show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def hide_window(self):
        self.withdraw()

    def quit_app(self):
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.engine.stop()
        try:
            self.quit()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
        sys.exit(0)

    # --- CONSTRUCCION DE LA INTERFAZ ---

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=THEME["bg_card"], height=58, corner_radius=0, border_width=1, border_color=THEME["border_light"])
        header.pack(fill="x")
        header.pack_propagate(False)

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=10)

        # Titulo limpio sin subtitulos redundantes
        titles = ctk.CTkFrame(inner, fg_color="transparent")
        titles.pack(side="left")

        ctk.CTkLabel(
            titles,
            text="Organizador de Archivos",
            font=(FONT_FAMILY, 17, "bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w")

        # Estado y boton de control
        ctrl_frame = ctk.CTkFrame(inner, fg_color="transparent")
        ctrl_frame.pack(side="right")

        # Badge con color de estado exclusivo (Verde activo / Ambar pausado)
        self.status_badge = ctk.CTkLabel(
            ctrl_frame,
            text="ACTIVO",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=THEME["status_active_text"][1],
            fg_color=THEME["status_active_bg"],
            corner_radius=6,
            padx=12,
            pady=4
        )
        self.status_badge.pack(side="left", padx=(0, 10))

        self.toggle_btn = ctk.CTkButton(
            ctrl_frame,
            text="Pausar",
            font=(FONT_FAMILY, 11),
            width=80,
            height=30,
            fg_color=THEME["btn_secondary_bg"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["btn_secondary_text"],
            border_width=1,
            border_color=THEME["btn_secondary_border"],
            corner_radius=6,
            command=self.toggle_monitoring
        )
        self.toggle_btn.pack(side="left")

    def _build_tab_bar(self):
        tab_container = ctk.CTkFrame(self, fg_color=THEME["tab_bar_bg"], height=38, corner_radius=8)
        tab_container.pack(fill="x", padx=20, pady=(12, 0))
        tab_container.pack_propagate(False)

        tabs = ["General", "Reglas", "Historial"]
        for t in tabs:
            btn = ctk.CTkButton(
                tab_container,
                text=t,
                font=(FONT_FAMILY, 12, "bold" if t == "General" else "normal"),
                height=30,
                corner_radius=6,
                command=lambda name=t: self._show_tab(name)
            )
            btn.pack(side="left", fill="both", expand=True, padx=3, pady=3)
            self.tab_buttons[t] = btn

        self._update_tab_button_styles("General")

    def _update_tab_button_styles(self, active_tab):
        for name, btn in self.tab_buttons.items():
            if name == active_tab:
                btn.configure(
                    fg_color=THEME["tab_active_bg"],
                    hover_color=THEME["tab_active_bg"],
                    text_color=THEME["tab_active_text"],
                    font=(FONT_FAMILY, 12, "bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=THEME["tab_hover_bg"],
                    text_color=THEME["tab_inactive_text"],
                    font=(FONT_FAMILY, 12, "normal")
                )

    def _build_content_area(self):
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True)

        # Construir las 3 vistas
        self.tab_frames["General"] = build_general_tab(self.content_area, self)
        self.tab_frames["Reglas"] = build_rules_tab(self.content_area, self)
        self.tab_frames["Historial"] = build_history_tab(self.content_area, self)

        # Mostrar la inicial
        self._show_tab("General")

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color=THEME["bg_card"], height=42, corner_radius=0, border_width=1, border_color=THEME["border_light"])
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        inner = ctk.CTkFrame(footer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=6)

        self.footer_info = ctk.CTkLabel(
            inner,
            text=f"Monitoreando: {self.engine.config.get('watch_dir', '')}",
            font=(FONT_FAMILY, 11),
            text_color=THEME["text_secondary"]
        )
        self.footer_info.pack(side="left")

        ctk.CTkButton(
            inner,
            text="Ocultar a bandeja",
            font=(FONT_FAMILY, 11),
            height=26,
            fg_color=THEME["btn_secondary_bg"],
            hover_color=THEME["btn_secondary_hover"],
            text_color=THEME["btn_secondary_text"],
            border_width=1,
            border_color=THEME["btn_secondary_border"],
            corner_radius=4,
            command=self.hide_window
        ).pack(side="right", padx=(8, 0))

        # Salir con rol destructivo exclusivo (Rojo #e0625a)
        ctk.CTkButton(
            inner,
            text="Salir",
            font=(FONT_FAMILY, 11, "bold"),
            height=26,
            fg_color="transparent",
            hover_color=THEME["action_danger_bg"],
            text_color=THEME["action_danger"],
            corner_radius=4,
            command=self.quit_app
        ).pack(side="right")

    def _show_tab(self, tab_name):
        self.current_tab = tab_name
        self._update_tab_button_styles(tab_name)
        for name, frame in self.tab_frames.items():
            if name == tab_name:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    # --- ACCIONES Y VISIBILIDAD DE PROCESO ---

    def browse_folder(self):
        current = self.engine.config.get("watch_dir", str(Path.home() / "Downloads"))
        selected = filedialog.askdirectory(initialdir=current, title="Seleccionar carpeta a monitorear")
        if selected:
            norm_selected = str(Path(selected))
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, norm_selected)
            success, msg = self.engine.set_watch_dir(norm_selected)
            self.footer_info.configure(text=f"Monitoreando: {norm_selected}")
            if not success:
                messagebox.showerror("Error", msg)

    def open_watch_folder(self):
        watch_dir = self.engine.config.get("watch_dir", "")
        if Path(watch_dir).exists():
            os.startfile(watch_dir)
        else:
            messagebox.showwarning("Advertencia", f"La carpeta no existe: {watch_dir}")

    def organize_now(self):
        # Desactivar temporalmente boton para prevenir clicks repetidos
        self.btn_organize_now.configure(state="disabled", text="Organizando...")
        
        # Mostrar contenedor de visibilidad de proceso
        self.process_progress_bar.pack(fill="x", pady=(0, 4))
        self.process_status_label.pack(fill="x")
        self.process_progress_bar.set(0)
        self.process_status_label.configure(
            text="Analizando carpeta...",
            text_color=THEME["text_secondary"]
        )

        def _task():
            count = self.engine.organize_now(on_progress=self._on_engine_progress)
            self.safe_after(lambda: self._finish_process_ui(count))

        threading.Thread(target=_task, daemon=True).start()

    def _on_engine_progress(self, current, total, filename):
        def _update():
            if total > 0:
                fraction = current / total
                self.process_progress_bar.set(fraction)
                self.process_status_label.configure(
                    text=f"Organizando {current}/{total} archivos: {filename}",
                    text_color=THEME["status_active"]
                )
        self.safe_after(_update)

    def _finish_process_ui(self, count):
        self.btn_organize_now.configure(state="normal", text="Organizar ahora")
        self.process_progress_bar.set(1.0)
        self.process_status_label.configure(
            text=f"Completado: {count} archivo(s) organizados",
            text_color=THEME["status_active"]
        )
        self.refresh_history_list()
        
        if self.engine.config.get("notifications", True):
            self._send_desktop_notification(
                "Organizador de Archivos",
                f"Organizacion completada: {count} archivo(s) ordenados."
            )

        # Ocultar indicador de progreso tras 4 segundos de inactividad
        if self._progress_reset_timer:
            self.after_cancel(self._progress_reset_timer)
        self._progress_reset_timer = self.after(4000, self._hide_process_ui)

    def _hide_process_ui(self):
        try:
            self.process_progress_bar.pack_forget()
            self.process_status_label.pack_forget()
            self.process_progress_bar.set(0)
            self.process_status_label.configure(text="")
        except Exception:
            pass

    def toggle_monitoring(self):
        if self.engine.is_running:
            self.engine.stop()
        else:
            threading.Thread(target=self.engine.start, daemon=True).start()

    def toggle_dark_mode(self):
        is_dark = self.dark_mode_var.get()
        new_theme = "dark" if is_dark else "light"
        ctk.set_appearance_mode(new_theme)
        self.engine.update_config(theme=new_theme)
        self.after(50, lambda: self._update_tab_button_styles(self.current_tab))

    def toggle_autostart(self):
        enabled = self.autostart_var.get()
        success = set_autostart(enabled)
        if success:
            self.engine.update_config(autostart=enabled)
        else:
            self.autostart_var.set(not enabled)
            messagebox.showerror("Error", "No se pudo actualizar el registro de inicio de Windows.")

    def save_general_preferences(self):
        self.engine.update_config(
            organize_on_start=self.retro_var.get(),
            notifications=self.notif_var.get()
        )

    # --- REGLAS / CATEGORIAS Y SUBCARPETAS ---

    def load_category_extensions(self):
        cat = self.rule_cat_var.get()
        categories = self.engine.config.get("categories", DEFAULT_CATEGORIES)
        exts = categories.get(cat, [])
        self.rule_ext_entry.delete("0.0", tk.END)
        self.rule_ext_entry.insert("0.0", ", ".join(exts))

    def save_current_category(self):
        cat = self.rule_cat_var.get()
        raw = self.rule_ext_entry.get("0.0", tk.END).strip()
        parsed = []
        for item in raw.split(","):
            cleaned = item.strip().lower()
            if cleaned:
                if not cleaned.startswith("."):
                    cleaned = f".{cleaned}"
                parsed.append(cleaned)
        categories = dict(self.engine.config.get("categories", DEFAULT_CATEGORIES))
        categories[cat] = sorted(list(set(parsed)))
        self.engine.update_config(categories=categories)
        messagebox.showinfo("Reglas actualizadas", f"Se guardaron las extensiones para '{cat}'.")

    def add_new_category(self):
        new_cat = self.new_cat_entry.get().strip()
        if not new_cat:
            messagebox.showwarning("Atencion", "Ingresa el nombre de la carpeta o subcarpeta (ej: Documentos/Facturas).")
            return
        
        new_cat = new_cat.replace("\\", "/").strip("/")
        categories = dict(self.engine.config.get("categories", DEFAULT_CATEGORIES))
        if new_cat in categories:
            messagebox.showwarning("Atencion", f"El destino '{new_cat}' ya existe.")
            return

        categories[new_cat] = []
        self.engine.update_config(categories=categories)
        self.new_cat_entry.delete(0, tk.END)

        updated_keys = list(categories.keys())
        self.rule_cat_menu.configure(values=updated_keys)
        self.rule_cat_var.set(new_cat)
        self.load_category_extensions()
        messagebox.showinfo("Subcarpeta creada", f"Se agrego '{new_cat}'. Ahora puedes asignarle extensiones.")

    def delete_current_category(self):
        cat = self.rule_cat_var.get()
        categories = dict(self.engine.config.get("categories", DEFAULT_CATEGORIES))
        if cat not in categories:
            return
        if len(categories) <= 1:
            messagebox.showwarning("Atencion", "Debe existir al menos una categoria.")
            return

        if messagebox.askyesno("Confirmar eliminacion", f"Eliminar el destino '{cat}'?"):
            del categories[cat]
            self.engine.update_config(categories=categories)
            updated_keys = list(categories.keys())
            self.rule_cat_menu.configure(values=updated_keys)
            self.rule_cat_var.set(updated_keys[0])
            self.load_category_extensions()

    def reset_categories(self):
        if messagebox.askyesno("Confirmar", "Restaurar las reglas y subcarpetas por defecto?"):
            self.engine.update_config(categories=DEFAULT_CATEGORIES)
            categories = list(DEFAULT_CATEGORIES.keys())
            self.rule_cat_menu.configure(values=categories)
            self.rule_cat_var.set(categories[0])
            self.load_category_extensions()

    # --- HISTORIAL ---

    def refresh_history_list(self):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        history = self.engine.history[-25:]
        if not history:
            ctk.CTkLabel(
                self.history_scroll,
                text="No hay movimientos registrados aun.",
                font=(FONT_FAMILY, 11),
                text_color=THEME["text_muted"]
            ).pack(pady=20)
            return

        for item in reversed(history):
            row = ctk.CTkFrame(self.history_scroll, fg_color=THEME["bg_card"], corner_radius=6, border_width=1, border_color=THEME["border"])
            row.pack(fill="x", padx=4, pady=3)

            ts = item.get("timestamp", "")
            time_str = ts.split("T")[1][:8] if "T" in ts else ts[:8]
            fname = item.get("filename", "")
            cat = item.get("category", "")

            # Badge hora neutro
            ctk.CTkLabel(
                row,
                text=time_str,
                font=(FONT_FAMILY, 10),
                text_color=THEME["text_muted"],
                fg_color=THEME["bg_card_sub"],
                corner_radius=4,
                padx=6,
                pady=2
            ).pack(side="left", padx=(8, 8), pady=6)

            # Nombre de archivo con alto contraste WCAG
            ctk.CTkLabel(
                row,
                text=fname,
                font=(FONT_FAMILY, 11, "bold"),
                text_color=THEME["text_primary"],
                anchor="w"
            ).pack(side="left")

            # Separador neutro
            ctk.CTkLabel(
                row,
                text="  ->  ",
                font=(FONT_FAMILY, 11),
                text_color=THEME["text_muted"]
            ).pack(side="left")

            # Destino
            ctk.CTkLabel(
                row,
                text=f"{cat}/",
                font=(FONT_FAMILY, 11),
                text_color=THEME["text_secondary"],
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

    def undo_last_action(self):
        success, msg = self.engine.undo_last()
        self.refresh_history_list()
        if success:
            messagebox.showinfo("Deshecho", msg)
        else:
            messagebox.showwarning("Atencion", msg)

    # --- CALLBACKS DEL MOTOR ---

    def _on_status_change(self, is_running):
        def _update():
            if is_running:
                # Color exclusivo de estado activo: Verde #38b487
                self.status_badge.configure(
                    text="ACTIVO",
                    fg_color=THEME["status_active_bg"],
                    text_color=THEME["status_active_text"][1]
                )
                self.toggle_btn.configure(text="Pausar")
            else:
                # Color exclusivo de estado pausado: Ambar #e0a53f
                self.status_badge.configure(
                    text="PAUSADO",
                    fg_color=THEME["status_paused_bg"],
                    text_color=THEME["status_paused_text"][1]
                )
                self.toggle_btn.configure(text="Reanudar")
        self.safe_after(_update)

    def _on_file_moved(self, entry):
        self.safe_after(self.refresh_history_list)
        if self.engine.config.get("notifications", True):
            self._send_desktop_notification(
                "Organizador de Archivos",
                f"{entry['filename']} movido a {entry['category']}/"
            )

    def _on_log(self, message):
        try:
            print(message)
        except Exception:
            pass

    def _send_desktop_notification(self, title, message):
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="Organizador de Archivos",
                timeout=3
            )
        except Exception:
            pass


if __name__ == "__main__":
    start_min = "--minimized" in sys.argv
    app = FileOrganizerApp(start_minimized=start_min)
    app.mainloop()
