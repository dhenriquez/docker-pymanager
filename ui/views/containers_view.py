import customtkinter as ctk
import threading
from typing import Dict, Any, List, Callable
from ..components.container_card import ContainerCard

class ContainersView(ctk.CTkFrame):
    """Containers view with search bar, running filter, and Compose project grouping."""

    def __init__(
        self,
        master,
        get_adapter_fn: Callable,
        on_view_logs: Callable[[str, str], None],
        on_open_shell: Callable[[str, str], None],
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.get_adapter_fn = get_adapter_fn
        self.on_view_logs = on_view_logs
        self.on_open_shell = on_open_shell

        # Header controls
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(16, 12))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="Contenedores",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f8fafc"
        )
        title_lbl.pack(side="left")

        # Reload button
        btn_reload = ctk.CTkButton(
            header_frame,
            text="⟳ Recargar",
            width=90,
            height=30,
            fg_color="#1e293b",
            hover_color="#334155",
            font=ctk.CTkFont(size=12),
            command=self.refresh
        )
        btn_reload.pack(side="right", padx=(10, 0))

        # Search box
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._apply_filters())
        self.search_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="🔍 Buscar contenedor, ID o proyecto...",
            textvariable=self.search_var,
            width=280,
            height=30,
            fg_color="#1e293b",
            border_color="#334155"
        )
        self.search_entry.pack(side="right", padx=10)

        # Only running toggle
        self.only_running_var = ctk.BooleanVar(value=False)
        self.running_switch = ctk.CTkSwitch(
            header_frame,
            text="Solo activos",
            variable=self.only_running_var,
            command=self._apply_filters,
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        self.running_switch.pack(side="right", padx=10)

        # Scrollable container list
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.containers_data: List[Dict[str, Any]] = []

    def refresh(self):
        """Fetches containers from active adapter in background thread."""
        threading.Thread(target=self._fetch_containers, daemon=True).start()

    def _fetch_containers(self):
        adapter = self.get_adapter_fn()
        if not adapter:
            return
        try:
            data = adapter.list_containers(all_containers=True)
            self.after(0, lambda: self._update_list(data))
        except Exception:
            pass

    def _update_list(self, data: List[Dict[str, Any]]):
        self.containers_data = data
        self._apply_filters()

    def _apply_filters(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        query = self.search_var.get().lower().strip()
        only_running = self.only_running_var.get()

        filtered = []
        for c in self.containers_data:
            if only_running and c["status"] != "running" and "Up" not in c["status"]:
                continue
            if query:
                match = (
                    query in c["name"].lower()
                    or query in c["image"].lower()
                    or query in c["compose_project"].lower()
                    or query in c["short_id"].lower()
                    or query in c["id"].lower()
                )
                if not match:
                    continue
            filtered.append(c)

        if not filtered:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="No se encontraron contenedores",
                font=ctk.CTkFont(size=14),
                text_color="#64748b"
            )
            empty_lbl.pack(pady=40)
            return

        # Agrupar por Compose Project
        compose_groups: Dict[str, List[Dict[str, Any]]] = {}
        standalone: List[Dict[str, Any]] = []

        for c in filtered:
            proj = c.get("compose_project")
            if proj:
                compose_groups.setdefault(proj, []).append(c)
            else:
                standalone.append(c)

        # Renderizar grupos de Compose con controles globales (Play/Stop/Delete)
        for proj_name, items in compose_groups.items():
            proj_box = ctk.CTkFrame(self.scroll_frame, fg_color="#0f172a", corner_radius=8)
            proj_box.pack(fill="x", pady=6)

            # Cabecera de proyecto
            header = ctk.CTkFrame(proj_box, fg_color="transparent")
            header.pack(fill="x", padx=12, pady=8)

            lbl_proj = ctk.CTkLabel(
                header,
                text=f"📁 {proj_name}  ({len(items)} contenedores)",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#38bdf8"
            )
            lbl_proj.pack(side="left")

            # Botones de accion global para todo el grupo Compose
            btn_group_frame = ctk.CTkFrame(header, fg_color="transparent")
            btn_group_frame.pack(side="right")

            # Boton Play para TODO el grupo
            btn_group_play = ctk.CTkButton(
                btn_group_frame,
                text="▶ Iniciar todos",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=100,
                height=26,
                fg_color="#10b981",
                hover_color="#059669",
                command=lambda items=items: self._run_group_action("start", items)
            )
            btn_group_play.pack(side="left", padx=3)

            # Boton Stop para TODO el grupo
            btn_group_stop = ctk.CTkButton(
                btn_group_frame,
                text="■ Detener",
                font=ctk.CTkFont(size=11),
                width=75,
                height=26,
                fg_color="#334155",
                hover_color="#475569",
                command=lambda items=items: self._run_group_action("stop", items)
            )
            btn_group_stop.pack(side="left", padx=3)

            # Contenedores hijos
            for item in items:
                card = ContainerCard(proj_box, container_data=item, on_action=self._handle_action)
                card.pack(fill="x", padx=10, pady=3)

        # Renderizar contenedores independientes
        if standalone:
            if compose_groups:
                sep_lbl = ctk.CTkLabel(
                    self.scroll_frame,
                    text="Contenedores Independientes",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#64748b"
                )
                sep_lbl.pack(anchor="w", pady=(12, 4), padx=4)

            for item in standalone:
                card = ContainerCard(self.scroll_frame, container_data=item, on_action=self._handle_action)
                card.pack(fill="x", pady=3)

    def _run_group_action(self, action: str, items: List[Dict[str, Any]]):
        adapter = self.get_adapter_fn()
        if not adapter:
            return

        def group_worker():
            for item in items:
                try:
                    c_id = item["id"]
                    if action == "start":
                        adapter.start_container(c_id)
                    elif action == "stop":
                        adapter.stop_container(c_id)
                except Exception:
                    pass
            self.after(500, self.refresh)

        threading.Thread(target=group_worker, daemon=True).start()

    def _handle_action(self, action: str, container_id: str):
        adapter = self.get_adapter_fn()
        if not adapter:
            return

        def run_action():
            try:
                if action == "start":
                    adapter.start_container(container_id)
                elif action == "stop":
                    adapter.stop_container(container_id)
                elif action == "restart":
                    adapter.restart_container(container_id)
                elif action == "delete":
                    adapter.remove_container(container_id, force=True)
                elif action == "logs":
                    c_name = container_id[:12]
                    for c in self.containers_data:
                        if c["id"] == container_id:
                            c_name = c["name"]
                            break
                    self.after(0, lambda: self.on_view_logs(container_id, c_name))
                    return
                elif action == "shell":
                    c_name = container_id[:12]
                    for c in self.containers_data:
                        if c["id"] == container_id:
                            c_name = c["name"]
                            break
                    self.after(0, lambda: self.on_open_shell(container_id, c_name))
                    return

                self.after(500, self.refresh)
            except Exception:
                pass

        threading.Thread(target=run_action, daemon=True).start()
