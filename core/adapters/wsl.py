import subprocess
import json
from typing import List, Dict, Any, Optional, Callable
import threading
from .base import DockerEngineAdapter

class WslEngineAdapter(DockerEngineAdapter):
    """
    Adapter connecting directly to Docker inside WSL2 (e.g. Ubuntu distro).
    Communicates via WSL command invocation using standard json output.
    """

    def __init__(self, distro: str = "Ubuntu"):
        self.distro = distro

    def get_name(self) -> str:
        return f"WSL2 Linux ({self.distro})"

    def _run_wsl_docker(self, args: List[str], timeout: int = 15) -> str:
        cmd = ["wsl", "-d", self.distro, "docker"] + args
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        )
        if res.returncode != 0:
            raise RuntimeError(res.stderr.strip() or f"WSL docker command exited with code {res.returncode}")
        return res.stdout

    def ping(self) -> bool:
        try:
            out = self._run_wsl_docker(["info", "--format", "{{json .ServerVersion}}"], timeout=5)
            return bool(out.strip())
        except Exception:
            return False

    def get_version(self) -> Dict[str, Any]:
        try:
            raw = self._run_wsl_docker(["version", "--format", "{{json .}}"])
            return json.loads(raw)
        except Exception as e:
            return {"Error": str(e), "Version": "WSL docker error"}

    def list_containers(self, all_containers: bool = True) -> List[Dict[str, Any]]:
        try:
            args = ["ps", "--format", "{{json .}}"]
            if all_containers:
                args.append("-a")

            output = self._run_wsl_docker(args)
            result = []
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    labels_str = item.get("Labels", "") or ""
                    compose_project = ""
                    for pair in labels_str.split(","):
                        if pair.startswith("com.docker.compose.project="):
                            compose_project = pair.split("=", 1)[1]
                            break

                    ports_val = item.get("Ports", "-") or "-"
                    result.append({
                        "id": item.get("ID", ""),
                        "short_id": item.get("ID", "")[:12],
                        "name": item.get("Names", "").lstrip("/"),
                        "image": item.get("Image", "<none>"),
                        "status": item.get("Status", ""),
                        "state": item.get("State", item.get("Status", "")),
                        "ports": ports_val,
                        "raw_ports": [p.strip() for p in ports_val.split(",") if p.strip()],
                        "compose_project": compose_project,
                        "created": item.get("CreatedAt", "")[:19]
                    })
                except Exception:
                    continue
            return result
        except Exception:
            return []

    def start_container(self, container_id: str) -> None:
        self._run_wsl_docker(["start", container_id])

    def stop_container(self, container_id: str) -> None:
        self._run_wsl_docker(["stop", "-t", "10", container_id])

    def restart_container(self, container_id: str) -> None:
        self._run_wsl_docker(["restart", "-t", "10", container_id])

    def remove_container(self, container_id: str, force: bool = False) -> None:
        args = ["rm"]
        if force:
            args.append("-f")
        args.append(container_id)
        self._run_wsl_docker(args)

    def stream_logs(
        self,
        container_id: str,
        line_callback: Callable[[str], None],
        stop_event: threading.Event,
        tail: int = 150
    ) -> None:
        cmd = ["wsl", "-d", self.distro, "docker", "logs", "--tail", str(tail), "-f", "-t", container_id]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        )

        try:
            for line in proc.stdout:
                if stop_event.is_set():
                    break
                line_callback(line.rstrip("\r\n"))
        finally:
            proc.kill()

    def list_images(self) -> List[Dict[str, Any]]:
        try:
            out = self._run_wsl_docker(["images", "--format", "{{json .}}"])
            result = []
            for line in out.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    result.append({
                        "id": data.get("ID", ""),
                        "short_id": data.get("ID", "")[:12],
                        "repo": data.get("Repository", "<none>"),
                        "tag": data.get("Tag", "<none>"),
                        "size_mb": 0.0,
                        "size_display": data.get("Size", "-"),
                        "created": data.get("CreatedAt", "")[:19],
                        "in_use": False
                    })
                except Exception:
                    continue
            return result
        except Exception:
            return []

    def remove_image(self, image_id: str, force: bool = False) -> None:
        args = ["rmi"]
        if force:
            args.append("-f")
        args.append(image_id)
        self._run_wsl_docker(args)

    def prune_images(self) -> Dict[str, Any]:
        out = self._run_wsl_docker(["image", "prune", "-f"])
        return {"Output": out}

    def list_volumes(self) -> List[Dict[str, Any]]:
        try:
            out = self._run_wsl_docker(["volume", "ls", "--format", "{{json .}}"])
            result = []
            for line in out.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    result.append({
                        "name": data.get("Name", ""),
                        "driver": data.get("Driver", "local"),
                        "created_at": "-",
                        "in_use": False
                    })
                except Exception:
                    continue
            return result
        except Exception:
            return []

    def remove_volume(self, volume_name: str, force: bool = False) -> None:
        args = ["volume", "rm"]
        if force:
            args.append("-f")
        args.append(volume_name)
        self._run_wsl_docker(args)

    def prune_volumes(self) -> Dict[str, Any]:
        out = self._run_wsl_docker(["volume", "prune", "-f"])
        return {"Output": out}

    def get_container_stats(self, container_id: str) -> Optional[Dict[str, Any]]:
        try:
            out = self._run_wsl_docker(["stats", "--no-stream", "--format", "{{json .}}", container_id])
            data = json.loads(out.strip())
            cpu_str = data.get("CPUPerc", "0%").rstrip("%")
            mem_str = data.get("MemPerc", "0%").rstrip("%")
            return {
                "cpu_percent": float(cpu_str) if cpu_str else 0.0,
                "mem_usage_mb": 0.0,
                "mem_limit_mb": 0.0,
                "mem_percent": float(mem_str) if mem_str else 0.0
            }
        except Exception:
            return None
