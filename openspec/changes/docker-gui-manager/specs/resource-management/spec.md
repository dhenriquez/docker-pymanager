## Purpose
Manages local Docker images and volumes, showing storage consumption, active usage states, and providing safe removal and prune capabilities.

## ADDED Requirements

### Requirement: Image Inventory and Usage Inspection
The system SHALL list all locally cached Docker images with their repository, tag, image ID, creation date, and disk size, indicating whether each image is actively referenced by any container.

#### Scenario: Active versus unused image indicator
- **WHEN** an image is referenced by at least one existing container
- **THEN** it displays an active (in-use) indicator dot, preventing accidental deletion

#### Scenario: Deleting an unused image
- **WHEN** user deletes an unused image
- **THEN** the system removes the image from local storage and updates the image list

### Requirement: Volume Inventory and Pruning
The system SHALL list all local volumes with their name, driver, estimated size, and in-use status.

#### Scenario: Pruning dangling volumes
- **WHEN** user executes volume prune
- **THEN** all unattached volumes are removed and reclaimed disk space is reported

