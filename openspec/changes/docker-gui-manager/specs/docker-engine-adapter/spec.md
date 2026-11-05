## Purpose
Provides unified connectivity and runtime switching between Docker Desktop (Windows Named Pipe) and WSL2 Docker engines with automatic discovery and health checking.

## ADDED Requirements

### Requirement: Multi-Engine Auto-Discovery
The system shall probe host endpoints to automatically detect available Docker engines on application startup.

#### Scenario: Docker Desktop is running
- **WHEN** the application starts and the Windows Named Pipe `\\.\pipe\docker_engine` is available and responsive
- **THEN** the system initializes the Docker client against Docker Desktop and sets it as the active engine

#### Scenario: Docker Desktop is inactive but WSL2 is available
- **WHEN** the Windows Named Pipe is not responsive, but WSL2 distro `Ubuntu` has an accessible Docker daemon (via CLI or TCP/socket)
- **THEN** the system switches to the WSL2 engine automatically and updates the status indicator to reflect the WSL2 backend

#### Scenario: No engine is available
- **WHEN** neither Docker Desktop nor WSL2 Docker daemons are reachable
- **THEN** the application displays a disconnected state with clear guidance on starting Docker Desktop or WSL2

### Requirement: Manual Engine Switching
The system shall provide a manual selector in the interface allowing users to switch the active Docker engine at runtime.

#### Scenario: User switches active engine
- **WHEN** the user selects a different engine from the status bar dropdown
- **THEN** the system closes existing client connections, initializes the selected engine, refreshes all view data, and logs any connection error without crashing

