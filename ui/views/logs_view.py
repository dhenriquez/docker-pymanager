import customtkinter as ctk
import threading
from typing import Callable, Optional

class LogsView(ctk.CTkFrame):
    """Live streaming log viewer with text searching, autoscroll toggle, and clear buffer."""

    def __init__(self, master, get_adapter_fn: Callable, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.get_adapter_fn = get_adapter_fn
        self.active_container_id: Optional[str] = None
        self._stop_event = threading.Event()
        self._stream_thread: Optional[threading.Thread] = None

        # Header controls
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(16, 12))

        self.title_lbl = ctk.CTkLabel(
            header_frame,
            text="Logs en Vivo",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f8fafc"
        )
        self.title_lbl.pack(side="left")

        self.container_badge = ctk.CTkLabel(
            header_frame,
            text="[Selecciona un contenedor]",
            font=ctk.CTkFont(size=12),
            text_color="#38bdf8",
            fg_color="#1e293b",
            corner_radius=4,
            padx=8,
            pady=3
        )
        self.container_badge.pack(side="left", padx=12)

        # Clear button
        btn_clear = ctk.CTkButton(
            header_frame,
            text="Limpiar",
            width=70,
            height=30,
            fg_color="#1e293b",
            hover_color="#334155",
            command=self.clear_logs
        )
        btn_clear.pack(side="right", padx=(8, 0))

        # Autoscroll switch
        self.autoscroll_var = ctk.BooleanVar(value=True)
        self.autoscroll_switch = ctk.CTkSwitch(
            header_frame,
            text="Autoscroll",
            variable=self.autoscroll_var,
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        self.autoscroll_switch.pack(side="right", padx=10)

        # Search box
        self.search_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="🔍 Filtrar logs...",
            width=200,
            height=30,
            fg_color="#1e293b",
            border_color="#334155"
        )
        self.search_entry.pack(side="right", padx=8)
        self.search_entry.bind("<KeyRelease>", self._filter_logs)

        # Text box for logs (monospace terminal style)
        self.log_textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#090d16",
            text_color="#cbd5e1",
            corner_radius=8,
            wrap="none"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.all_lines = []

    def start_streaming(self, container_id: str, container_name: str):
        """Starts streaming logs for the specified container."""
        self.stop_streaming()
        self.active_container_id = container_id
        self.container_badge.configure(text=f"📦 {container_name}")
        self.clear_logs()

        self._stop_event.clear()
        self._stream_thread = threading.Thread(
            target=self._stream_worker,
            args=(container_id,),
            daemon=True
        )
        self._stream_thread.start()

    def stop_streaming(self):
        self._stop_event.set()
        if self._stream_thread and self._stream_thread.is_alive():
            self._stream_thread.join(timeout=0.5)

    def _stream_worker(self, container_id: str):
        adapter = self.get_adapter_fn()
        if not adapter:
            return

        def append_line(line: str):
            self.after(0, lambda: self._add_line(line))

        adapter.stream_logs(container_id, append_line, self._stop_event)

    def _add_line(self, line: str):
        self.all_lines.append(line)
        query = self.search_entry.get().lower().strip()
        if not query or query in line.lower():
            self.log_textbox.insert("end", line + "\n")
            if self.autoscroll_var.get():
                self.log_textbox.see("end")

    def _filter_logs(self, event=None):
        query = self.search_entry.get().lower().strip()
        self.log_textbox.delete("1.0", "end")
        for line in self.all_lines:
            if not query or query in line.lower():
                self.log_textbox.insert("end", line + "\n")
        if self.autoscroll_var.get():
            self.log_textbox.see("end")

    def clear_logs(self):
        self.all_lines = []
        self.log_textbox.delete("1.0", "end")

