import customtkinter as ctk
from typing import Callable, List, Dict, Any

class StatusBar(ctk.CTkFrame):
    """Bottom status bar with engine selector, engine status dot, and system telemetry."""

    def __init__(
        self,
        master,
        engine_options: List[str],
        current_engine: str,
        on_engine_change: Callable[[str], None],
        **kwargs
    ):
        super().__init__(master, height=36, corner_radius=0, fg_color="#0b0f19", **kwargs)
        self.on_engine_change = on_engine_change

        # Left status indicator
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.pack(side="left", padx=16)

        self.status_dot = ctk.CTkLabel(
            left_frame,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color="#10b981"
        )
        self.status_dot.pack(side="left", padx=(0, 6))

        self.status_text = ctk.CTkLabel(
            left_frame,
            text="Engine running",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94a3b8"
        )
        self.status_text.pack(side="left", padx=(0, 16))

        # Engine selector dropdown
        lbl_switch = ctk.CTkLabel(
            left_frame,
            text="Motor:",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        )
        lbl_switch.pack(side="left", padx=(0, 6))

        self.engine_dropdown = ctk.CTkOptionMenu(
            left_frame,
            values=engine_options,
            command=self._on_switch,
            width=210,
            height=24,
            corner_radius=4,
            font=ctk.CTkFont(size=11),
            fg_color="#1e293b",
            button_color="#334155",
            button_hover_color="#475569",
            dropdown_fg_color="#1e293b"
        )
        self.engine_dropdown.set(current_engine)
        self.engine_dropdown.pack(side="left")

        # Right telemetry display
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.pack(side="right", padx=16)

        self.telemetry_label = ctk.CTkLabel(
            self.right_frame,
            text="RAM: -- GB  |  CPU: --%  |  Disco: -- GB libre",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        )
        self.telemetry_label.pack(side="right")

    def _on_switch(self, selected_engine: str):
        self.on_engine_change(selected_engine)

    def update_status(self, is_online: bool, engine_name: str):
        if is_online:
            self.status_dot.configure(text_color="#10b981")
            self.status_text.configure(text=f"Conectado: {engine_name}", text_color="#10b981")
        else:
            self.status_dot.configure(text_color="#ef4444")
            self.status_text.configure(text="Desconectado", text_color="#ef4444")

    def update_telemetry(self, data: Dict[str, Any]):
        text = (
            f"RAM: {data.get('mem_used_gb', 0)} GB / {data.get('mem_total_gb', 0)} GB ({data.get('mem_percent', 0)}%)  |  "
            f"CPU: {data.get('cpu_percent', 0)}%  |  "
            f"Disco: {data.get('disk_free_gb', 0)} GB disp."
        )
        self.telemetry_label.configure(text=text)

