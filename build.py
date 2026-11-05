import PyInstaller.__main__
import os
import sys

def build():
    print("Iniciando empaquetado de Docker PyManager como UN SOLO ARCHIVO (.exe independiente)...")

    root_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(root_dir, "app.py")

    args = [
        app_path,
        "--name=DockerPyManager",
        "--noconsole",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--collect-all=customtkinter",
        "--hidden-import=docker",
        "--hidden-import=psutil",
        "--hidden-import=requests",
        "--hidden-import=urllib3",
        f"--paths={root_dir}",
    ]

    print("Ejecutando PyInstaller con argumentos:", " ".join(args))
    PyInstaller.__main__.run(args)
    print("\n[✓] ¡Empaquetado completado exitosamente en dist/DockerPyManager.exe!")

if __name__ == "__main__":
    build()
