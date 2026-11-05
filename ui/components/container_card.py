import customtkinter as ctk
import webbrowser
from typing import Dict, Any, Callable

class ContainerCard(ctk.CTkFrame):
    """Renders a single container row with status dot, ID, info, ports, and action buttons."""

    def __init__(
        self,
        master,
        container_data: Dict[str, Any],
        on_action: Callable[[str, str], None],
        **kwargs
    ):
        super().__init__(master, fg_color="#182234", corner_radius=6, height=44, **kwargs)
        self.container_data = container_data
        self.container_id = container_data["id"]
        self.short_id = container_data.get("short_id", self.container_id[:12])
        self.on_action = on_action

        self.grid_columnconfigure(1, weight=1)

        # 0. Status Dot
        is_running = container_data["status"] == "running" or "Up" in container_data["status"]
        status_color = "#10b981" if is_running else "#64748b"

        dot_label = ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color=status_color,
            width=24
        )
        dot_label.grid(row=0, column=0, padx=(10, 2), pady=6, sticky="w")

        # 1. Name & Container ID badge (clickable to copy to clipboard)
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        name_label = ctk.CTkLabel(
            info_frame,
            text=container_data["name"],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f1f5f9"
        )
        name_label.pack(side="left")

        # Container ID Button (Click para copiar)
        self.id_btn = ctk.CTkButton(
            info_frame,
            text=f"📋 {self.short_id}",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#94a3b8",
            fg_color="#0f172a",
            hover_color="#1e293b",
            corner_radius=4,
            height=22,
            width=80,
            command=self._copy_id_to_clipboard
        )
        self.id_btn.pack(side="left", padx=(8, 0))

        img_label = ctk.CTkLabel(
            info_frame,
            text=f"({container_data['image']})",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        )
        img_label.pack(side="left", padx=(6, 0))

        # 2. Ports with clickable links
        ports_str = container_data.get("ports", "-")
        ports_frame = ctk.CTkFrame(self, fg_color="transparent")
        ports_frame.grid(row=0, column=2, padx=12, pady=6, sticky="w")

        if ports_str and ports_str != "-":
            for port_pair in ports_str.split(", "):
                btn_port = ctk.CTkButton(
                    ports_frame,
                    text=f"{port_pair} ↗",
                    font=ctk.CTkFont(size=11),
                    height=24,
                    fg_color="#0f172a",
                    hover_color="#1e293b",
                    text_color="#38bdf8",
                    corner_radius=4,
                    command=lambda p=port_pair: self._open_port(p)
                )
                btn_port.pack(side="left", padx=2)
        else:
            no_port_label = ctk.CTkLabel(
                ports_frame,
                text="Sin puertos",
                font=ctk.CTkFont(size=11),
                text_color="#64748b"
            )
            no_port_label.pack(side="left")

        # 3. Status text
        status_label = ctk.CTkLabel(
            self,
            text=container_data["status"],
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8",
            width=130,
            anchor="w"
        )
        status_label.grid(row=0, column=3, padx=10, pady=6)

        # 4. Action Buttons: Start / Stop / Restart / Exec-Shell / Logs / Delete
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=0, column=4, padx=(6, 12), pady=6, sticky="e")

        if is_running:
            btn_stop = ctk.CTkButton(
                btn_frame,
                text="■",
                width=28,
                height=28,
                corner_radius=4,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#334155",
                hover_color="#475569",
                command=lambda: self.on_action("stop", self.container_id)
            )
            btn_stop.pack(side="left", padx=2)

            btn_restart = ctk.CTkButton(
                btn_frame,
                text="🔄",
                width=28,
                height=28,
                corner_radius=4,
                font=ctk.CTkFont(size=11),
                fg_color="#334155",
                hover_color="#475569",
                command=lambda: self.on_action("restart", self.container_id)
            )
            btn_restart.pack(side="left", padx=2)
        else:
            btn_start = ctk.CTkButton(
                btn_frame,
                text="▶",
                width=28,
                height=28,
                corner_radius=4,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#10b981",
                hover_color="#059669",
                command=lambda: self.on_action("start", self.container_id)
            )
            btn_start.pack(side="left", padx=2)

        # Shell button (Símbolo de sistema / CLI interactivo directo al contenedor)
        btn_shell = ctk.CTkButton(
            btn_frame,
            text=">_",
            width=28,
            height=28,
            corner_radius=4,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#0369a1" if is_running else "#1e293b",
            hover_color="#0284c7" if is_running else "#334155",
            text_color="#f0f9ff" if is_running else "#64748b",
            state="normal" if is_running else "disabled",
            command=lambda: self.on_action("shell", self.container_id)
        )
        btn_shell.pack(side="left", padx=2)

        # Logs button
        btn_logs = ctk.CTkButton(
            btn_frame,
            text="📋",
            width=28,
            height=28,
            corner_radius=4,
            font=ctk.CTkFont(size=11),
            fg_color="#334155",
            hover_color="#38bdf8",
            command=lambda: self.on_action("logs", self.container_id)
        )
        btn_logs.pack(side="left", padx=2)

        # Delete button
        btn_del = ctk.CTkButton(
            btn_frame,
            text="🗑",
            width=28,
            height=28,
            corner_radius=4,
            font=ctk.CTkFont(size=11),
            fg_color="#450a0a",
            hover_color="#dc2626",
            command=lambda: self.on_action("delete", self.container_id)
        )
        btn_del.pack(side="left", padx=2)

    def _copy_id_to_clipboard(self):
        """Copia el ID completo o corto al portapapeles y da feedback visual inmediato."""
        try:
            self.clipboard_clear()
            self.clipboard_append(self.short_id)
            self.update() # necesario para procesar el portapapeles en Tkinter

            # Feedback visual
            original_text = f"📋 {self.short_id}"
            self.id_btn.configure(text="✓ Copiado!", fg_color="#065f46", text_color="#34d399")
            self.after(1400, lambda: self.id_btn.configure(text=original_text, fg_color="#0f172a", text_color="#94a3b8"))
        except Exception:
            pass

    def _open_port(self, port_str: str):
        try:
            host_part = port_str.split(":")[0] if ":" in port_str else port_str
            if "->" in host_part:
                host_part = host_part.split("->")[0]
            if ":" in host_part:
                host_part = host_part.split(":")[-1]

            port_num = int("".join(filter(str.isdigit, host_part)))
            url = f"http://localhost:{port_num}"
            webbrowser.open(url)
        except Exception:
            pass
