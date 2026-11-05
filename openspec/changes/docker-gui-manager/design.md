## Context

See `proposal.md` for overall motivation and goals.
The target environment is Windows 10/11 with WSL2 installed (Ubuntu distro) and optionally Docker Desktop. Existing containers (such as `moodle53-mariadb`, `moodle53-app`, and `rea-ghidra-sandbox`) run on the host Docker daemon. The application will be written in Python and compiled into a standalone Windows executable (`.exe`).

## Goals / Non-Goals

**Goals:**
- Provide a clean, dark-mode desktop GUI built with `CustomTkinter` mirroring the visual clarity of Docker Desktop.
- Support both Docker Desktop (Windows Named Pipe `\\.\pipe\docker_engine`) and WSL2 Docker engines with auto-detection and runtime switching.
- Enable full lifecycle control of containers (start, stop, restart, delete) with Docker Compose hierarchy visualization.
- Deliver non-blocking live log streaming with search and autoscroll.
- Display memory and CPU metrics using background polling threads.
- Package as a single `.exe` file without external runtime dependencies via PyInstaller.

**Non-Goals:**
- Not building an in-engine virtualization hypervisor or kernel replacement (delegates to Docker Engine/WSL2).
- Not managing Kubernetes clusters or cloud registries in this MVP.
- Not implementing a container image editor or Dockerfile visual composer.

## Decisions

### 1. GUI Framework: CustomTkinter
- **Decision**: Use `CustomTkinter` on Python 3.10+.
- **Rationale**: Delivers modern rounded widgets, dark mode palette (deep slate/navy matching Docker Desktop), and scales cleanly on Windows high-DPI displays while remaining 100% native Python without browser engine overhead.
- **Alternatives Considered**:
  - `PyQt6` / `PySide6`: Heavier binary size (~100MB+), stricter licensing.
  - `PyWebView`: Requires managing a local web server or web assets; higher memory overhead.

### 2. Multi-Engine Architecture & Adapter Pattern
- **Decision**: Define an abstract `DockerEngineAdapter` interface implemented by `DesktopEngineAdapter` and `WslEngineAdapter`.
- **Details**:
  - `DesktopEngineAdapter`: Connects to `npipe:////./pipe/docker_engine` using `docker.DockerClient`.
  - `WslEngineAdapter`: Connects to WSL2 either via `tcp://127.0.0.1:2375` (if exposed), unix socket forwarder, or invokes `wsl -d Ubuntu docker` commands via JSON formatting fallback.
  - `EngineManager`: Probes endpoints sequentially during startup, sets active adapter, and emits change events to the UI.
- **Alternatives Considered**: Direct single-socket hardcoding (would fail if Docker Desktop is stopped).

### 3. Concurrency & Threading Model
- **Decision**: Use Python `threading.Thread` with daemon workers and `queue.Queue` or `root.after()` dispatch for UI updates.
- **Details**:
  - `LogStreamWorker`: Consumes generator from `container.logs(stream=True, follow=True)` in a background thread, queuing lines to update the Tkinter Text widget safely on the main thread.
  - `MetricsWorker`: Polls container stats (`container.stats(stream=False)`) periodically every 3 seconds without blocking UI responsiveness.
- **Alternatives Considered**: `asyncio` loop intertwined with Tkinter mainloop (higher complexity and thread-safety caveats with CustomTkinter).

### 4. Project Structure
```text
rea-docker/
├── app.py                     # Main application entry point
├── build.py                   # PyInstaller build automation script
├── requirements.txt           # Project dependencies
├── core/
│   ├── engine_manager.py      # Multi-engine auto-discovery & switcher
│   ├── adapters/
│   │   ├── base.py            # Base DockerEngineAdapter
│   │   ├── desktop.py         # Windows Named Pipe adapter
│   │   └── wsl.py             # WSL2 adapter
│   └── telemetry.py           # Background CPU/RAM metrics collector
└── ui/
    ├── app_window.py          # Main CustomTkinter window & layout
    ├── components/
    │   ├── sidebar.py         # Navigation sidebar
    │   ├── status_bar.py      # Engine selector & resource bar
    │   └── container_card.py  # Compose group & container row widgets
    └── views/
        ├── containers_view.py # Containers list & Compose tree
        ├── logs_view.py       # Live logs modal / viewer
        ├── images_view.py     # Images table & actions
        └── volumes_view.py    # Volumes table & prune
```

## Risks / Trade-offs

- **[Risk] CustomTkinter assets missing in PyInstaller build**:
  - *Mitigation*: Specify `--collect-all customtkinter` and explicit data hooks in `build.py`.
- **[Risk] UI freeze during slow Docker daemon responses or network timeouts**:
  - *Mitigation*: All calls to `client.containers.list()`, `start()`, `stop()`, etc., are executed in worker threads or short-timeout guards with loading spinners.
- **[Risk] WSL2 port forwarding and socket accessibility**:
  - *Mitigation*: Adapter checks availability gracefully and guides user to enable WSL2 Docker integration if connection is refused.

