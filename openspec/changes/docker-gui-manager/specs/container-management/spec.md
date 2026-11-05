## Purpose
Enables comprehensive container lifecycle control, Docker Compose project grouping, live status tracking, and browser navigation for mapped ports.

## ADDED Requirements

### Requirement: Container Listing and Compose Grouping
The system SHALL list all containers and group containers that belong to the same Docker Compose project under a collapsible project header.

#### Scenario: Compose project grouping
- **WHEN** containers share a common `com.docker.compose.project` label
- **THEN** they are rendered nested under a project parent node with project-level summary and bulk controls

#### Scenario: Standalone container listing
- **WHEN** containers do not belong to any Compose project
- **THEN** they are listed directly in the standalone container section

### Requirement: Container Lifecycle Actions
The system SHALL allow users to start, stop, restart, and delete containers directly from the table or detail view.

#### Scenario: Stopping a running container
- **WHEN** user clicks the stop button on an active container
- **THEN** the system issues a stop request, updates the status badge to stopping/exited, and refreshes the container row

#### Scenario: Starting a stopped container
- **WHEN** user clicks the start button on an exited container
- **THEN** the system issues a start command and updates the status badge to running with green indicator

#### Scenario: Deleting a container
- **WHEN** user clicks the delete button and confirms removal
- **THEN** the container is removed from Docker and removed from the active view

### Requirement: Port Redirection
The system SHALL display all published container ports and allow launching the corresponding URL in the user's default browser.

#### Scenario: Clicking a published port
- **WHEN** a container exposes port `8080:80` and the user clicks on the port label
- **THEN** the system opens `http://localhost:8080` in the default host web browser

### Requirement: Real-Time Search and Filtering
The system SHALL filter the visible container list according to search keywords and status filters.

#### Scenario: Only show running filter
- **WHEN** the user toggles the "Only show running containers" switch
- **THEN** exited and paused containers are hidden from the list view

