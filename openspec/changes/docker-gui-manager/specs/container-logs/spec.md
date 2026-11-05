## Purpose
Provides asynchronous live log streaming, text searching, and display controls for any selected Docker container.

## ADDED Requirements

### Requirement: Real-Time Log Streaming
The system SHALL stream container stdout and stderr in real-time without blocking the user interface thread.

#### Scenario: Viewing live container logs
- **WHEN** user selects a container and opens its logs view
- **THEN** recent log lines are fetched and new incoming lines are appended as they arrive from the Docker daemon

### Requirement: Log Search and Filtering
The system SHALL allow filtering displayed logs by text queries.

#### Scenario: Searching in logs
- **WHEN** user types a search string into the log search input
- **THEN** non-matching log lines are hidden or matching segments are highlighted in real-time

### Requirement: Autoscroll and Clear Logs
The system SHALL support toggling autoscroll to the latest log line and clearing the local log buffer.

#### Scenario: Autoscroll enabled
- **WHEN** new log entries arrive and autoscroll is enabled
- **THEN** the log viewer automatically scrolls to the newest line at the bottom

