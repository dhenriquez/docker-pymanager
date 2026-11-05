## Purpose
Delivers a responsive, dark-themed native desktop interface built with CustomTkinter, system resource monitoring, and a self-contained Windows executable build.

## ADDED Requirements

### Requirement: Modern Dark Theme Interface
The system SHALL render a dark theme styled interface resembling Docker Desktop with a navigation sidebar, main content view, and bottom status bar.

#### Scenario: Navigating views
- **WHEN** user clicks on navigation items (Containers, Images, Volumes) in the sidebar
- **THEN** the main panel switches smoothly to the selected view while preserving background monitoring

### Requirement: System Resource Telemetry
The system SHALL display real-time CPU and Memory utilization of the host and container engine in the header and status bar.

#### Scenario: Updating resource metrics
- **WHEN** background polling runs every few seconds
- **THEN** total container CPU percentage and memory footprint are recalculated and refreshed in the header without UI stutter

### Requirement: Standalone Executable Packaging
The system SHALL provide packaging automation using PyInstaller to bundle the application into a single `.exe` file runnable without an external Python runtime.

#### Scenario: Running compiled executable
- **WHEN** the bundled `.exe` is executed on Windows
- **THEN** it launches directly without a console command prompt window and connects to the available Docker daemon

