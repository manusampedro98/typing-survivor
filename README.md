# Typing Survivor

Typing Survivor es un videojuego de mecanografía desarrollado con Python y Pygame. El objetivo será escribir correctamente las palabras asociadas a los enemigos antes de que alcancen al jugador.

El proyecto se está construyendo de forma incremental para practicar organización de código, programación orientada a objetos, gestión de estados, eventos de teclado y desarrollo de videojuegos 2D.

## Estado actual

El proyecto dispone de una ventana principal y un bucle de juego estable a 60 FPS.
La aplicación procesa los eventos del sistema y actualiza la pantalla en cada fotograma.

El desarrollo de las mecánicas se encuentra en progreso.

## Tecnologías

- Python 3.12
- Pygame 2.6.1
- Conda para gestionar el entorno
- Git para el control de versiones

## Estructura del proyecto

```text
typing-survivor/
├── assets/
│   ├── fonts/           # Fuentes de texto
│   ├── images/          # Imágenes y sprites
│   └── sounds/          # Música y efectos de sonido
├── data/                # Listas de palabras y otros datos
├── game/
│   └── __init__.py      # Paquete para los módulos del juego
├── .gitignore           # Archivos excluidos del repositorio
├── main.py              # Punto de entrada
├── README.md            # Documentación
└── requirements.txt     # Dependencias de Python
```

Los archivos `.gitkeep` permiten conservar en Git las carpetas que todavía están vacías.

## Preparación del entorno

Abre una terminal dentro de la carpeta del proyecto y crea un entorno Conda con Python 3.12:

```powershell
conda create --name typing-survivor python=3.12 pip
conda activate typing-survivor
python -m pip install -r requirements.txt
```

En VS Code, selecciona como intérprete el entorno Conda `typing-survivor`.

## Ejecución

Activa el entorno y ejecuta el punto de entrada:

```powershell
conda activate typing-survivor
python main.py
```

Al ejecutar el proyecto se abrirá la ventana principal del juego. Puedes cerrarla mediante el botón de cierre de la ventana.
