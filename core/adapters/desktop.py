import docker
from typing import List, Dict, Any, Optional, Callable
import threading
from .base import DockerEngineAdapter

class DesktopEngineAdapter(DockerEngineAdapter):
    """Adapter connecting to Docker Desktop via Windows Named Pipe: \\\\.\\pipe\\docker_engine."""

    def __init__(self, base_url: str = "npipe:////./pipe/docker_engine"):
        self.base_url = base_url
        self._client: Optional[docker.DockerClient] = None

    def _get_client(self) -> docker.DockerClient:
        if self._client is None:
            self._client = docker.DockerClient(base_url=self.base_url, timeout=5)
        return self._client

    def get_name(self) -> str:
        return "Docker Desktop (Windows Pipe)"

    def ping(self) -> bool:
        try:
            client = self._get_client()
            return bool(client.ping())
        except Exception:
            self._client = None
            return False

    def get_version(self) -> Dict[str, Any]:
        try:
            return self._get_client().version()
        except Exception as e:
            return {"Error": str(e), "Version": "Desconocido"}

    def list_containers(self, all_containers: bool = True) -> List[Dict[str, Any]]:
        client = self._get_client()
        raw_containers = client.containers.list(all=all_containers)
        result = []

        for c in raw_containers:
            attrs = c.attrs
            labels = attrs.get("Config", {}).get("Labels") or {}
            compose_project = labels.get("com.docker.compose.project", "")

            # Formatear puertos
            network_settings = attrs.get("NetworkSettings", {})
            raw_ports = network_settings.get("Ports") or {}
            formatted_ports = []
            for container_port, host_bindings in raw_ports.items():
                if host_bindings:
                    for binding in host_bindings:
                        host_ip = binding.get("HostIp", "")
                        host_port = binding.get("HostPort", "")
                        formatted_ports.append(f"{host_port}:{container_port}")
                else:
                    formatted_ports.append(container_port)

            image_tags = c.image.tags if c.image.tags else [c.attrs.get("Config", {}).get("Image", "<sin tag>")]

            result.append({
                "id": c.id,
                "short_id": c.short_id,
                "name": c.name.lstrip("/"),
                "image": image_tags[0] if image_tags else "<none>",
                "status": c.status,
                "state": attrs.get("State", {}).get("Status", c.status),
                "ports": ", ".join(formatted_ports) if formatted_ports else "-",
                "raw_ports": formatted_ports,
                "compose_project": compose_project,
                "created": attrs.get("Created", "")[:19].replace("T", " "),
            })

        return result

    def start_container(self, container_id: str) -> None:
        self._get_client().containers.get(container_id).start()

    def stop_container(self, container_id: str) -> None:
        self._get_client().containers.get(container_id).stop(timeout=10)

    def restart_container(self, container_id: str) -> None:
        self._get_client().containers.get(container_id).restart(timeout=10)

    def remove_container(self, container_id: str, force: bool = False) -> None:
        self._get_client().containers.get(container_id).remove(force=force)

    def stream_logs(
        self,
        container_id: str,
        line_callback: Callable[[str], None],
        stop_event: threading.Event,
        tail: int = 150
    ) -> None:
        try:
            container = self._get_client().containers.get(container_id)
            # Primero enviar las ultimas lineas
            initial_logs = container.logs(tail=tail, timestamps=True).decode("utf-8", errors="replace")
            for line in initial_logs.splitlines():
                if stop_event.is_set():
                    return
                line_callback(line)

            # Stream continuo
            for chunk in container.logs(stream=True, follow=True, timestamps=True):
                if stop_event.is_set():
                    break
                line = chunk.decode("utf-8", errors="replace").rstrip("\r\n")
                line_callback(line)
        except Exception as e:
            if not stop_event.is_set():
                line_callback(f"[Error de streaming logs: {e}]")

    def list_images(self) -> List[Dict[str, Any]]:
        client = self._get_client()
        raw_images = client.images.list()
        active_image_ids = {c.image.id for c in client.containers.list(all=True)}

        result = []
        for img in raw_images:
            tags = img.tags if img.tags else ["<none>:<none>"]
            tag_display = tags[0]
            repo, tag = tag_display.split(":", 1) if ":" in tag_display else (tag_display, "")
            size_mb = round(img.attrs.get("Size", 0) / (1024 * 1024), 2)
            created = img.attrs.get("Created", "")[:19].replace("T", " ")

            result.append({
                "id": img.id,
                "short_id": img.short_id.replace("sha256:", "")[:12],
                "repo": repo,
                "tag": tag,
                "size_mb": size_mb,
                "size_display": f"{size_mb} MB" if size_mb < 1024 else f"{round(size_mb/1024, 2)} GB",
                "created": created,
                "in_use": img.id in active_image_ids
            })
        return result

    def remove_image(self, image_id: str, force: bool = False) -> None:
        self._get_client().images.remove(image_id, force=force)

    def prune_images(self) -> Dict[str, Any]:
        return self._get_client().images.prune(filters={"dangling": False})

    def list_volumes(self) -> List[Dict[str, Any]]:
        client = self._get_client()
        raw_volumes = client.volumes.list()

        # Determinar que volumenes estan montados en contenedores
        used_volumes = set()
        for c in client.containers.list(all=True):
            for mount in c.attrs.get("Mounts", []):
                if mount.get("Type") == "volume":
                    used_volumes.add(mount.get("Name"))

        result = []
        for v in raw_volumes:
            v_name = v.name
            attrs = v.attrs
            result.append({
                "name": v_name,
                "driver": attrs.get("Driver", "local"),
                "created_at": attrs.get("CreatedAt", "")[:19].replace("T", " "),
                "in_use": v_name in used_volumes
            })
        return result

    def remove_volume(self, volume_name: str, force: bool = False) -> None:
        self._get_client().volumes.get(volume_name).remove(force=force)

    def prune_volumes(self) -> Dict[str, Any]:
        return self._get_client().volumes.prune()

    def get_container_stats(self, container_id: str) -> Optional[Dict[str, Any]]:
        try:
            container = self._get_client().containers.get(container_id)
            stats = container.stats(stream=False)
            
            # Calcular uso de CPU
            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})
            cpu_delta = cpu_stats.get("cpu_usage", {}).get("total_usage", 0) - precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
            system_delta = cpu_stats.get("system_cpu_usage", 0) - precpu_stats.get("system_cpu_usage", 0)
            online_cpus = cpu_stats.get("online_cpus", 1) or 1

            cpu_percent = 0.0
            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * online_cpus * 100.0

            # Calcular uso de RAM
            mem_stats = stats.get("memory_stats", {})
            usage = mem_stats.get("usage", 0)
            limit = mem_stats.get("limit", 1)
            mem_percent = (usage / limit) * 100.0 if limit > 0 else 0.0

            return {
                "cpu_percent": round(cpu_percent, 2),
                "mem_usage_mb": round(usage / (1024 * 1024), 2),
                "mem_limit_mb": round(limit / (1024 * 1024), 2),
                "mem_percent": round(mem_percent, 2)
            }
        except Exception:
            return None

