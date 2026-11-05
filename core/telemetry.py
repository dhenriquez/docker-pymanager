import psutil
import threading
import time
from typing import Callable, Dict, Any

class TelemetryWorker:
    """Periodically collects host and engine CPU and RAM telemetry."""

    def __init__(self, update_callback: Callable[[Dict[str, Any]], None], interval_sec: float = 3.0):
        self.update_callback = update_callback
        self.interval_sec = interval_sec
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                cpu_percent = psutil.cpu_percent(interval=None)
                virtual_mem = psutil.virtual_memory()
                disk = psutil.disk_usage("/")

                data = {
                    "cpu_percent": round(cpu_percent, 1),
                    "mem_used_gb": round(virtual_mem.used / (1024**3), 2),
                    "mem_total_gb": round(virtual_mem.total / (1024**3), 2),
                    "mem_percent": round(virtual_mem.percent, 1),
                    "disk_free_gb": round(disk.free / (1024**3), 1),
                    "disk_total_gb": round(disk.total / (1024**3), 1),
                }
                self.update_callback(data)
            except Exception:
                pass
            time.sleep(self.interval_sec)

