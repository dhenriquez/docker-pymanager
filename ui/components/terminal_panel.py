import customtkinter as ctk
import subprocess
import threading
import os
import queue

class TerminalPanel(ctk.CTkFrame):
    """
    Embedded interactive terminal panel matching Docker Desktop bottom console.
    Executes PowerShell or bash commands, or directly attaches to containers.
    """

    def __init__(self, master, on_close_callback=None, **kwargs):
        super().__init__(master, fg_color="#090d16", corner_radius=8, **kwargs)
        self.on_close_callback = on_close_callback
        self.process: subprocess.Popen = None
        self.output_queue = queue.Queue()
        self.is_running = True

        # Header bar
        header = ctk.CTkFrame(self, fg_color="#0f172a", height=32, corner_radius=0)
        header.pack(fill="x")

        self.title_lbl = ctk.CTkLabel(
            header,
            text=">_ Terminal (PowerShell / Docker CLI)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8"
        )
        self.title_lbl.pack(side="left", padx=12, pady=4)

        # Quick action buttons inside terminal
        btn_cls = ctk.CTkButton(
            header,
            text="Limpiar",
            width=60,
            height=22,
            font=ctk.CTkFont(size=11),
            fg_color="#1e293b",
            hover_color="#334155",
            command=self.clear_output
        )
        btn_cls.pack(side="right", padx=(4, 8), pady=4)

        if on_close_callback:
            btn_close = ctk.CTkButton(
                header,
                text="✕",
                width=26,
                height=22,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#334155",
                hover_color="#ef4444",
                command=self.on_close_callback
            )
            btn_close.pack(side="right", padx=4, pady=4)

        # Output text area (Terminal style)
        self.textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#090d16",
            text_color="#e2e8f0",
            wrap="char",
            corner_radius=0
        )
        self.textbox.pack(fill="both", expand=True, padx=8, pady=(4, 0))

        # Input line at bottom
        input_frame = ctk.CTkFrame(self, fg_color="#0f172a", height=34, corner_radius=0)
        input_frame.pack(fill="x", side="bottom")

        self.prompt_lbl = ctk.CTkLabel(
            input_frame,
            text="PS >",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color="#10b981"
        )
        self.prompt_lbl.pack(side="left", padx=(10, 4))

        self.entry = ctk.CTkEntry(
            input_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#1e293b",
            border_color="#334155",
            placeholder_text="Escribe un comando (ej: docker ps, docker logs <id>)..."
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(4, 10), pady=4)
        self.entry.bind("<Return>", self._on_enter)

        # Start background queue reader
        self.after(100, self._check_queue)
        self._print_line("=== Terminal Integrada iniciada (Docker PyManager) ===")
        self._print_line("Puedes ejecutar cualquier comando docker o interactuar directamente.")
        self._print_line("---------------------------------------------------------------")

    def _print_line(self, line: str):
        self.textbox.insert("end", line + "\n")
        self.textbox.see("end")

    def clear_output(self):
        self.textbox.delete("1.0", "end")

    def run_command(self, cmd_str: str):
        self._print_line(f"\n{self.prompt_lbl.cget('text')} {cmd_str}")
        threading.Thread(target=self._exec_worker, args=(cmd_str,), daemon=True).start()

    def _exec_worker(self, cmd_str: str):
        try:
            # Ejecutar con powershell
            p = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", cmd_str],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
            )
            for line in p.stdout:
                self.output_queue.put(line.rstrip("\r\n"))
            p.wait()
        except Exception as e:
            self.output_queue.put(f"[Error: {e}]")

    def _on_enter(self, event=None):
        cmd = self.entry.get().strip()
        if not cmd:
            return
        self.entry.delete(0, "end")
        self.run_command(cmd)

    def _check_queue(self):
        while not self.output_queue.empty():
            try:
                line = self.output_queue.get_nowait()
                self._print_line(line)
            except Exception:
                break
        self.after(50, self._check_queue)

    def launch_container_shell_in_new_window(self, container_id: str, container_name: str, engine_name: str):
        """
        Opens a standalone native Windows terminal window executing an interactive shell
        (bash or sh) inside the container using 'docker exec -it <id> sh'.
        """
        self._print_line(f"[*] Abriendo consola interactiva para el contenedor '{container_name}'...")
        try:
            if "WSL" in engine_name:
                cmd = f'start cmd /k "wsl -d Ubuntu docker exec -it {container_id} sh || wsl -d Ubuntu docker exec -it {container_id} bash"'
            else:
                cmd = f'start cmd /k "docker exec -it {container_id} sh || docker exec -it {container_id} bash"'
            os.system(cmd)
        except Exception as e:
            self._print_line(f"[-] Error abriendo terminal: {e}")

