## Why

Docker Desktop requires commercial licensing for larger teams and consumes considerable system resources on Windows. Developers need a lightweight, native, and customizable graphical desktop application to manage Docker containers, images, volumes, and live logs across both Docker Desktop (Windows Named Pipe) and native WSL2 environments, distributable as a standalone Windows executable (`.exe`).

## What Changes

- Create a modern dark-themed desktop application built with `CustomTkinter` replicating key Docker Desktop management workflows.
- Implement a multi-engine connection layer supporting automatic engine detection and runtime switching between Docker Desktop (`\\.\pipe\docker_engine`) and WSL2 (`Ubuntu` socket / CLI).
- Provide container management with automatic Docker Compose project grouping, status indicators, port navigation shortcuts, and lifecycle actions (start, stop, restart, delete).
- Implement real-time container log streaming with searching, timestamp toggling, and auto-scroll.
- Add views for local images and volumes, showing sizes, usage state (active vs. dangling/unused), and cleanup capabilities.
- Provide PyInstaller packaging scripts to build a single standalone `.exe` without console windows.

## Capabilities

### New Capabilities
- `docker-engine-adapter`: Discovers, connects to, and dynamically switches between Docker Desktop (Windows Named Pipe) and WSL2 Docker engines with automatic fallback.
- `container-management`: Inventories containers, groups them by Docker Compose projects, exposes container actions (start/stop/restart/remove), and provides port redirection.
- `container-logs`: Asynchronous real-time log streaming for selected containers with filtering and text search.
- `resource-management`: Inventories images and volumes, determines container association/usage, and executes removal and pruning operations.
- `desktop-gui`: CustomTkinter dark-mode desktop window with responsive layouts, navigation sidebar, and PyInstaller bundling specification.

### Modified Capabilities
<!-- None -->

## Impact

- New Python project codebase in `c:\Users\dhenriquez\Documents\Sitios\rea-docker`.
- Dependencies: `customtkinter`, `docker`, `psutil`, `pyinstaller`.
- Interacts with host Docker Named Pipes, WSL2 CLI/sockets, and local web browser for port shortcuts.

