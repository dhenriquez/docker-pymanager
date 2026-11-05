## 1. Project Setup and Dependencies

- [x] 1.1 Create virtual environment / dependency manifest `requirements.txt` with `customtkinter`, `docker`, `psutil`, and `pyinstaller`, and verify packages import correctly.
- [x] 1.2 Initialize project directory layout (`core/`, `core/adapters/`, `ui/`, `ui/components/`, `ui/views/`) and verify the module structure exists.

## 2. Core Docker Multi-Engine Adapters & Telemetry

- [x] 2.1 Implement `core/adapters/base.py` defining the `DockerEngineAdapter` abstract interface (containers, images, volumes, logs, stats).
- [x] 2.2 Implement `core/adapters/desktop.py` connecting via Windows Named Pipe `\\.\pipe\docker_engine` and verify connection to active containers.
- [x] 2.3 Implement `core/adapters/wsl.py` providing auto-detection and connection fallback to WSL2 Ubuntu engine.
- [x] 2.4 Implement `core/engine_manager.py` managing auto-discovery, active engine state, and dynamic engine switching.
- [x] 2.5 Implement `core/telemetry.py` background worker polling system and container CPU/RAM utilization and verify thread safety.

## 3. UI Framework and Layout Base

- [x] 3.1 Implement `ui/app_window.py` creating the main `CustomTkinter` dark-mode container window with grid geometry.
- [x] 3.2 Implement `ui/components/sidebar.py` with navigation buttons (Containers, Images, Volumes) and app branding.
- [x] 3.3 Implement `ui/components/status_bar.py` with engine status indicator, engine switch dropdown, and host telemetry gauges.

## 4. Container Management View & Compose Grouping

- [x] 4.1 Implement `ui/components/container_card.py` rendering individual container rows with status dots, port links, and control buttons (start, stop, restart, delete).
- [x] 4.2 Implement `ui/views/containers_view.py` with search filtering, "Only show running" toggle switch, and automatic Docker Compose project collapsible tree grouping.
- [x] 4.3 Implement port shortcut handling to open published ports in the default web browser.

## 5. Live Logs Streaming & Search

- [x] 5.1 Implement background thread log streaming worker in `core/adapters/base.py` and adapter implementations using non-blocking queues.
- [x] 5.2 Implement `ui/views/logs_view.py` with text searching, timestamp toggle, autoscroll switch, and clear buffer action.

## 6. Images and Volumes Management

- [x] 6.1 Implement `ui/views/images_view.py` displaying image name, tag, ID, size, in-use indicator, and image deletion.
- [x] 6.2 Implement `ui/views/volumes_view.py` displaying volume name, driver, size, in-use indicator, and volume prune action.

## 7. Build Automation and Executable Packaging

- [x] 7.1 Create `build.py` packaging script configuring PyInstaller with `--windowed`, `--collect-all customtkinter`, and icon bundling.
- [x] 7.2 Execute PyInstaller build and verify that `dist/DockerPyManager.exe` starts and successfully controls containers without a terminal prompt.
