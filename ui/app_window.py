import customtkinter as ctk
from typing import Optional

from core.engine_manager import EngineManager
from core.telemetry import TelemetryWorker
from .components.sidebar import Sidebar
from .components.status_bar import StatusBar
from .components.terminal_panel import TerminalPanel
from .views.containers_view import ContainersView
from .views.images_view import ImagesView
from .views.volumes_view import VolumesView
from .views.logs_view import LogsView

class AppWindow(ctk.CTk):
    """Main application window container for Docker PyManager."""

    def __init__(self, engine_manager: EngineManager):
        super().__init__()

        self.engine_manager = engine_manager
        self.title("Docker PyManager — Container & Image Dashboard")
        self.geometry("1180x750")
        self.minsize(950, 620)

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color="#0e131f")

        # Grid configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) # terminal drawer / status bar
        self.grid_columnconfigure(0, weight=0) # sidebar
        self.grid_columnconfigure(1, weight=1) # content view

        # 1. Sidebar
        self.sidebar = Sidebar(self, on_navigate=self.show_view)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. Main content container
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Bottom drawer for embedded terminal
        self.terminal_panel = TerminalPanel(self.content_frame, on_close_callback=self._close_terminal_drawer)
        self.is_terminal_open = False

        # Initialize views
        self.views = {
            "containers": ContainersView(
                self.content_frame,
                get_adapter_fn=self.engine_manager.get_active_engine,
                on_view_logs=self.open_logs_for_container,
                on_open_shell=self.open_shell_for_container
            ),
            "images": ImagesView(
                self.content_frame,
                get_adapter_fn=self.engine_manager.get_active_engine
            ),
            "volumes": VolumesView(
                self.content_frame,
                get_adapter_fn=self.engine_manager.get_active_engine
            ),
            "logs": LogsView(
                self.content_frame,
                get_adapter_fn=self.engine_manager.get_active_engine
            ),
            "terminal": self.terminal_panel
        }

        # 3. Status Bar
        current_eng_name = self.engine_manager.get_active_engine().get_name() if self.engine_manager.get_active_engine() else "Ninguno"
        self.status_bar = StatusBar(
            self,
            engine_options=self.engine_manager.get_available_engine_names(),
            current_engine=current_eng_name,
            on_engine_change=self._on_engine_switched
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Telemetry worker
        self.telemetry = TelemetryWorker(update_callback=self._on_telemetry_data)
        self.telemetry.start()

        # Engine listener
        self.engine_manager.add_listener(self._on_engine_updated)

        # Show initial view
        self.show_view("containers")

        # Protocol for clean exit
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def show_view(self, view_name: str):
        if view_name == "terminal":
            self._show_terminal_drawer()
            return

        for name, view in self.views.items():
            if name == view_name:
                view.grid(row=0, column=0, sticky="nsew")
                if hasattr(view, "refresh"):
                    view.refresh()
            else:
                if name != "terminal":
                    view.grid_forget()

    def _show_terminal_drawer(self):
        # Muestra la terminal integrada ocupando la mitad inferior o pantalla completa
        self.terminal_panel.grid(row=0, column=0, sticky="nsew")
        for name, view in self.views.items():
            if name != "terminal":
                view.grid_forget()

    def _close_terminal_drawer(self):
        self.terminal_panel.grid_forget()
        self.sidebar._highlight("containers")
        self.show_view("containers")

    def open_logs_for_container(self, container_id: str, container_name: str):
        self.sidebar._highlight("logs")
        self.show_view("logs")
        logs_view: LogsView = self.views["logs"]
        logs_view.start_streaming(container_id, container_name)

    def open_shell_for_container(self, container_id: str, container_name: str):
        """
        Ejecuta un símbolo del sistema / terminal interactivo conectado directamente al contenedor
        usando 'docker exec -it <id> sh' en una consola nativa visible e interactiva.
        """
        active_engine = self.engine_manager.get_active_engine()
        engine_name = active_engine.get_name() if active_engine else ""
        self.terminal_panel.launch_container_shell_in_new_window(container_id, container_name, engine_name)

    def _on_engine_switched(self, engine_name: str):
        success = self.engine_manager.set_active_engine(engine_name)
        if success:
            active = self.engine_manager.get_active_engine()
            is_online = active.ping() if active else False
            self.status_bar.update_status(is_online, engine_name)
            for view in self.views.values():
                if hasattr(view, "refresh") and view.winfo_ismapped():
                    view.refresh()

    def _on_engine_updated(self, adapter):
        is_online = adapter.ping()
        self.status_bar.update_status(is_online, adapter.get_name())

    def _on_telemetry_data(self, data):
        self.after(0, lambda: self.status_bar.update_telemetry(data))

    def _on_close(self):
        self.telemetry.stop()
        logs_view: LogsView = self.views["logs"]
        logs_view.stop_streaming()
        self.destroy()
