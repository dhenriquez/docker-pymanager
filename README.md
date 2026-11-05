# Docker PyManager 🐳

<p align="center">
  <b>Una alternativa gráfica moderna, nativa y ligera a Docker Desktop para Windows y WSL2</b><br>
  Construida en Python con <code>CustomTkinter</code> y empaquetada como un único ejecutable <code>.exe</code> portátil.
</p>

---

## 💡 ¿Por qué Docker PyManager?

Docker Desktop para Windows suele requerir licencias de pago para organizaciones medianas/grandes y consume cantidades considerables de memoria RAM en segundo plano. 

**Docker PyManager** nace como una alternativa de código abierto, ultraligera y rápida, diseñada para gestionar tus contenedores tanto si estás usando **Docker Desktop** como si estás usando **Docker nativo en WSL2 (Ubuntu)** de forma 100% independiente.

---

## ✨ Características Principales

- 🎨 **Interfaz Moderna en Modo Oscuro (`CustomTkinter`):**
  - Paleta de diseño basada en la interfaz oficial de Docker Desktop (tonos slate/navy, bordes redondeados y fuentes claras).
  - Cero dependencias de navegadores web (sin Electron) para un inicio instantáneo y mínimo consumo de CPU/RAM.

- 🔄 **Soporte Multi-Motor Híbrido:**
  - **Docker Desktop (Windows):** Comunicación nativa mediante el Windows Named Pipe `\\.\pipe\docker_engine`.
  - **WSL2 Linux (`Ubuntu`):** Conexión directa con el motor Docker ejecutándose en WSL2 sin necesidad de abrir Docker Desktop.
  - **Auto-detección Inteligente:** Detecta el motor disponible al iniciar y permite alternar entre ellos en caliente mediante un selector en la barra de estado.

- 📦 **Gestión Completa de Contenedores:**
  - **Visualización de IDs:** Muestra el ID corto (`short_id`) al estilo Docker Desktop junto al nombre del contenedor.
  - **Agrupación por Docker Compose:** Los contenedores pertenecientes a un mismo archivo Compose se agrupan automáticamente bajo un encabezado colapsable con controles en lote.
  - **Botón ▶ Iniciar todos / ■ Detener:** Inicia o detiene todos los contenedores de un proyecto Compose con un solo clic.
  - **Acceso Directo a Puertos (`8080:80 ↗`):** Abre la URL correspondiente en tu navegador web con un solo clic.
  - **Controles de Ciclo de Vida:** Iniciar, Detener, Reiniciar y Eliminar contenedores.
  - **Filtros en Tiempo Real:** Búsqueda instantánea por nombre, imagen o ID, y switch para mostrar *"Solo activos"*.

- 💻 **Consola Interactiva y Terminal Integrada:**
  - **Botón `>_` por Contenedor:** Abre al instante una terminal nativa interactiva ejecutando `docker exec -it <id> sh` / `bash` dentro del contenedor.
  - **Pestaña `>_ Terminal`:** Consola embebida en la propia aplicación para ejecutar comandos rápidos de PowerShell o Docker CLI.

- 📋 **Visor de Logs en Vivo:**
  - Streaming de logs en tiempo real sin congelar la interfaz gráfica.
  - Búsqueda y filtrado de texto dentro del log, toggle de autoscroll y botón de limpieza.

- 🖼️ **Imágenes y 💾 Volúmenes:**
  - Listado detallado con tamaños legibles y marcas visuales de estado (en uso activo vs. huérfanos/dangling).
  - Botón de limpieza en lote (*Prune*) para recuperar espacio en disco con un clic.

- 📊 **Telemetría del Sistema:**
  - Monitor en vivo de consumo de CPU, RAM total y espacio libre en disco en la barra inferior.

---

## 🚀 Descarga y Ejecución (.exe)

No necesitas tener Python instalado en tu máquina. El proyecto se compila en un único ejecutable portable:

1. Ve a la carpeta `dist/`.
2. Ejecuta haciendo doble clic en:
   ```text
   DockerPyManager.exe
   ```

---

## 🛠️ Desarrollo y Ejecución desde Código Fuente

Si deseas modificar o extender la aplicación:

### 1. Clonar el repositorio
```bash
git clone https://github.com/dhenriquez/docker-pymanager.git
cd docker-pymanager
```

### 2. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación
```powershell
python app.py
```

### 4. Compilar el ejecutable (.exe)
Para generar el binario único empaquetado:
```powershell
python build.py
```
El archivo resultante se creará automáticamente en `dist/DockerPyManager.exe`.

---

## 📂 Estructura del Proyecto

```text
docker-pymanager/
├── app.py                     # Punto de entrada principal
├── build.py                   # Script de empaquetado con PyInstaller (--onefile)
├── requirements.txt           # Dependencias del proyecto
├── core/
│   ├── engine_manager.py      # Gestor de auto-detección y conmutación de motores
│   ├── telemetry.py           # Hilo de telemetría de recursos del sistema
│   └── adapters/
│       ├── base.py            # Interfaz abstracta DockerEngineAdapter
│       ├── desktop.py         # Adaptador para Docker Desktop (Windows Named Pipe)
│       └── wsl.py             # Adaptador para WSL2 Ubuntu (Socket / CLI)
└── ui/
    ├── app_window.py          # Ventana principal de CustomTkinter
    ├── components/
    │   ├── sidebar.py         # Barra lateral de navegación
    │   ├── status_bar.py      # Barra de estado y selector de motor
    │   ├── terminal_panel.py  # Panel de terminal integrada
    │   └── container_card.py  # Tarjeta de fila de contenedor con ID y acciones
    └── views/
        ├── containers_view.py # Vista principal de contenedores y proyectos Compose
        ├── logs_view.py       # Visor de logs en streaming
        ├── images_view.py     # Vista de imágenes y prune
        └── volumes_view.py    # Vista de volúmenes y prune
```

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.
