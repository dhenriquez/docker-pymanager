import sys
from core.engine_manager import EngineManager
from ui.app_window import AppWindow

def main():
    # Inicializar gestor de motores con auto-detección
    engine_manager = EngineManager()

    # Iniciar ventana principal de la interfaz
    app = AppWindow(engine_manager)
    app.mainloop()

if __name__ == "__main__":
    main()

