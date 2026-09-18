# Typing Survivor

Typing Survivor es un videojuego de mecanografía desarrollado con Python y Pygame. El objetivo será escribir correctamente las palabras asociadas a los enemigos antes de que alcancen al jugador.

El proyecto se está construyendo de forma incremental para practicar organización de código, programación orientada a objetos, gestión de estados, eventos de teclado y desarrollo de videojuegos 2D.

## Estado actual

El proyecto dispone de una ventana principal, un bucle de juego estable a 60 FPS y
un ciclo jugable básico para escribir y completar palabras objetivo.

El desarrollo de las mecánicas se encuentra en progreso.

## Características actuales

- Entrada de texto compatible con la distribución del teclado.
- Campo de escritura con cursor parpadeante.
- Borrado continuo al mantener pulsada la tecla Retroceso.
- Palabras objetivo cargadas desde un archivo externo.
- Comparación visual de caracteres correctos e incorrectos.
- Selección automática de una nueva palabra al completar la actual.
- Contador de palabras completadas durante la sesión.
- Cierre mediante el botón de la ventana o la tecla Escape.

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
├── data/
│   └── words.txt        # Palabras disponibles durante la partida
├── game/
│   ├── __init__.py      # Define el paquete del juego
│   ├── game.py          # Controlador y bucle principal
│   ├── settings.py      # Configuración visual y general
│   └── word_manager.py  # Carga y selección de palabras
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

Al ejecutar el proyecto aparecerá una palabra objetivo. Cada carácter se marcará según
coincida con el objetivo y, al completar la palabra, se seleccionará una nueva
automáticamente. Puedes borrar con Retroceso y cerrar mediante Escape o el botón de la
ventana.
