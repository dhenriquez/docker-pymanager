import customtkinter as ctk
import threading
from typing import Dict, Any, List, Callable

class VolumesView(ctk.CTkFrame):
    """View listing Docker volumes with driver, in-use indicator, deletion, and prune."""

    def __init__(self, master, get_adapter_fn: Callable, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.get_adapter_fn = get_adapter_fn
        self.volumes_data: List[Dict[str, Any]] = []

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 12))

        title = ctk.CTkLabel(
            header,
            text="Volúmenes",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f8fafc"
        )
        title.pack(side="left")

        btn_reload = ctk.CTkButton(
            header,
            text="⟳ Recargar",
            width=90,
            height=30,
            fg_color="#1e293b",
            hover_color="#334155",
            command=self.refresh
        )
        btn_reload.pack(side="right", padx=(8, 0))

        btn_prune = ctk.CTkButton(
            header,
            text="🧹 Limpiar no usados",
            width=140,
            height=30,
            fg_color="#450a0a",
            hover_color="#dc2626",
            command=self._prune_volumes
        )
        btn_prune.pack(side="right", padx=8)

        # Scrollable table
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def refresh(self):
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        adapter = self.get_adapter_fn()
        if not adapter:
            return
        try:
            data = adapter.list_volumes()
            self.after(0, lambda: self._render(data))
        except Exception:
            pass

    def _render(self, data: List[Dict[str, Any]]):
        self.volumes_data = data
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        if not data:
            empty = ctk.CTkLabel(self.scroll_frame, text="No hay volúmenes creados", font=ctk.CTkFont(size=14), text_color="#64748b")
            empty.pack(pady=40)
            return

        for vol in data:
            row = ctk.CTkFrame(self.scroll_frame, fg_color="#182234", corner_radius=6, height=40)
            row.pack(fill="x", pady=3)
            row.grid_columnconfigure(1, weight=1)

            # In use status
            dot_color = "#10b981" if vol.get("in_use") else "#64748b"
            dot = ctk.CTkLabel(row, text="●", font=ctk.CTkFont(size=14), text_color=dot_color, width=28)
            dot.grid(row=0, column=0, padx=(12, 4), pady=6, sticky="w")

            # Name
            name_lbl = ctk.CTkLabel(row, text=vol["name"], font=ctk.CTkFont(size=13, weight="bold"), text_color="#f1f5f9", anchor="w")
            name_lbl.grid(row=0, column=1, padx=6, pady=6, sticky="w")

            # Driver
            driver_lbl = ctk.CTkLabel(row, text=f"driver: {vol['driver']}", font=ctk.CTkFont(size=11), text_color="#64748b", width=120)
            driver_lbl.grid(row=0, column=2, padx=10, pady=6)

            # Delete button
            btn_del = ctk.CTkButton(
                row,
                text="🗑",
                width=28,
                height=28,
                corner_radius=4,
                font=ctk.CTkFont(size=11),
                fg_color="#450a0a",
                hover_color="#dc2626",
                command=lambda v_name=vol["name"]: self._delete_volume(v_name)
            )
            btn_del.grid(row=0, column=3, padx=(6, 12), pady=6, sticky="e")

    def _delete_volume(self, volume_name: str):
        adapter = self.get_adapter_fn()
        if not adapter:
            return
        def worker():
            try:
                adapter.remove_volume(volume_name, force=True)
                self.after(500, self.refresh)
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def _prune_volumes(self):
        adapter = self.get_adapter_fn()
        if not adapter:
            return
        def worker():
            try:
                adapter.prune_volumes()
                self.after(500, self.refresh)
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

