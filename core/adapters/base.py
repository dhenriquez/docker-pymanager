from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
import threading

class DockerEngineAdapter(ABC):
    """Abstract interface for Docker engine backends (Docker Desktop and WSL2)."""

    @abstractmethod
    def get_name(self) -> str:
        """Returns human-readable engine name."""
        pass

    @abstractmethod
    def ping(self) -> bool:
        """Returns True if the engine is responding."""
        pass

    @abstractmethod
    def get_version(self) -> Dict[str, Any]:
        """Returns Docker engine version information dictionary."""
        pass

    @abstractmethod
    def list_containers(self, all_containers: bool = True) -> List[Dict[str, Any]]:
        """
        Returns list of container metadata dictionaries.
        Each item includes: id, short_id, name, image, status, state, ports, compose_project, created.
        """
        pass

    @abstractmethod
    def start_container(self, container_id: str) -> None:
        """Starts a stopped container."""
        pass

    @abstractmethod
    def stop_container(self, container_id: str) -> None:
        """Stops a running container."""
        pass

    @abstractmethod
    def restart_container(self, container_id: str) -> None:
        """Restarts a container."""
        pass

    @abstractmethod
    def remove_container(self, container_id: str, force: bool = False) -> None:
        """Removes a container."""
        pass

    @abstractmethod
    def stream_logs(
        self,
        container_id: str,
        line_callback: Callable[[str], None],
        stop_event: threading.Event,
        tail: int = 100
    ) -> None:
        """Streams container logs line by line via callback."""
        pass

    @abstractmethod
    def list_images(self) -> List[Dict[str, Any]]:
        """
        Returns list of images.
        Each item includes: id, short_id, tags, size, created, in_use.
        """
        pass

    @abstractmethod
    def remove_image(self, image_id: str, force: bool = False) -> None:
        """Deletes a local image."""
        pass

    @abstractmethod
    def prune_images(self) -> Dict[str, Any]:
        """Removes unused images."""
        pass

    @abstractmethod
    def list_volumes(self) -> List[Dict[str, Any]]:
        """
        Returns list of volumes.
        Each item includes: name, driver, created_at, size, in_use.
        """
        pass

    @abstractmethod
    def remove_volume(self, volume_name: str, force: bool = False) -> None:
        """Removes a volume."""
        pass

    @abstractmethod
    def prune_volumes(self) -> Dict[str, Any]:
        """Removes all unused local volumes."""
        pass

    @abstractmethod
    def get_container_stats(self, container_id: str) -> Optional[Dict[str, Any]]:
        """Returns single-shot CPU and RAM usage for a container."""
        pass

