from typing import List, Optional, Callable
from .adapters.base import DockerEngineAdapter
from .adapters.desktop import DesktopEngineAdapter
from .adapters.wsl import WslEngineAdapter

class EngineManager:
    """Manages active Docker engine and provides switching and event callbacks."""

    def __init__(self):
        self.adapters: List[DockerEngineAdapter] = [
            DesktopEngineAdapter(),
            WslEngineAdapter(distro="Ubuntu")
        ]
        self.active_adapter: Optional[DockerEngineAdapter] = None
        self._listeners: List[Callable[[DockerEngineAdapter], None]] = []
        self.auto_detect()

    def auto_detect(self) -> Optional[DockerEngineAdapter]:
        """Probes adapters in priority order and sets the first responsive one."""
        for adapter in self.adapters:
            if adapter.ping():
                self.set_active_engine(adapter.get_name())
                return self.active_adapter
        # Fallback to first even if not currently pinging
        if self.adapters:
            self.active_adapter = self.adapters[0]
        return self.active_adapter

    def get_available_engine_names(self) -> List[str]:
        return [a.get_name() for a in self.adapters]

    def get_active_engine(self) -> Optional[DockerEngineAdapter]:
        return self.active_adapter

    def set_active_engine(self, engine_name: str) -> bool:
        for adapter in self.adapters:
            if adapter.get_name() == engine_name:
                self.active_adapter = adapter
                self._notify_listeners()
                return True
        return False

    def add_listener(self, callback: Callable[[DockerEngineAdapter], None]) -> None:
        self._listeners.append(callback)

    def _notify_listeners(self) -> None:
        if self.active_adapter:
            for cb in self._listeners:
                try:
                    cb(self.active_adapter)
                except Exception:
                    pass

