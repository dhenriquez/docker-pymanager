import customtkinter as ctk
from typing import Callable

class Sidebar(ctk.CTkFrame):
    """Left navigation sidebar modeled after Docker Desktop."""

    def __init__(self, master, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(master, width=220, corner_radius=0, fg_color="#111927", **kwargs)
        self.on_navigate = on_navigate
        self.buttons = {}

        # Brand header
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(18, 24))

        logo_label = ctk.CTkLabel(
            brand_frame,
            text="🐳 docker.py",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#38bdf8"
        )
        logo_label.pack(side="left")

        tag_label = ctk.CTkLabel(
            brand_frame,
            text="DESKTOP",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color="#94a3b8",
            fg_color="#1e293b",
            corner_radius=4,
            padx=6,
            pady=2
        )
        tag_label.pack(side="left", padx=(8, 0))

        # Navigation buttons
        nav_items = [
            ("containers", "📦  Contenedores"),
            ("images", "🖼️  Imágenes"),
            ("volumes", "💾  Volúmenes"),
            ("logs", "📋  Logs en Vivo"),
            ("terminal", ">_  Terminal"),
        ]

        for key, text in nav_items:
            btn = ctk.CTkButton(
                self,
                text=text,
                anchor="w",
                font=ctk.CTkFont(size=13, weight="normal"),
                fg_color="transparent",
                text_color="#cbd5e1",
                hover_color="#1e293b",
                height=40,
                corner_radius=6,
                command=lambda k=key: self._on_btn_click(k)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.buttons[key] = btn

        # Default select
        self._highlight("containers")

    def _on_btn_click(self, key: str):
        self._highlight(key)
        self.on_navigate(key)

    def _highlight(self, selected_key: str):
        for key, btn in self.buttons.items():
            if key == selected_key:
                btn.configure(fg_color="#1e293b", text_color="#38bdf8", font=ctk.CTkFont(size=13, weight="bold"))
            else:
                btn.configure(fg_color="transparent", text_color="#94a3b8", font=ctk.CTkFont(size=13, weight="normal"))
