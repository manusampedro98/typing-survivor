# Typing Survivor

Typing Survivor es un videojuego de mecanografía desarrollado con Python y Pygame. El objetivo será escribir correctamente las palabras asociadas a los enemigos antes de que alcancen al jugador.

El proyecto se está construyendo de forma incremental para practicar organización de código, programación orientada a objetos, gestión de estados, eventos de teclado y desarrollo de videojuegos 2D.

## Estado actual

El proyecto dispone de una ventana principal, un bucle de juego estable a 60 FPS y
un primer ciclo de supervivencia contra enemigos asociados a palabras.

El desarrollo de las mecánicas se encuentra en progreso.

## Características actuales

- Entrada de texto compatible con la distribución del teclado.
- Campo de escritura con cursor parpadeante.
- Menú inicial y pausa durante la partida.
- Borrado continuo al mantener pulsada la tecla Retroceso.
- Palabras objetivo cargadas desde un archivo externo.
- Comparación visual de caracteres correctos e incorrectos.
- Selección automática de una nueva palabra al completar la actual.
- Enemigo móvil con velocidad independiente de los FPS.
- Enemigos normales, rápidos y blindados con comportamientos diferentes.
- Contador de enemigos eliminados desglosado por tipo.
- Eliminación del enemigo al completar su palabra.
- Sistema de tres vidas y registro de palabras completadas y falladas.
- Puntuación basada en la longitud de cada palabra.
- Combo de aciertos con multiplicador progresivo.
- Cálculo en tiempo real de PPM, precisión y errores de escritura.
- Oleadas con aumento gradual y limitado de la velocidad enemiga.
- Pantalla de fin de partida con reinicio mediante la tecla R.
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
│   ├── armored_enemy.py # Variante resistente de dos palabras
│   ├── enemy.py         # Movimiento y representación del enemigo
│   ├── enemy_type.py    # Identificadores de las variantes enemigas
│   ├── fast_enemy.py    # Variante rápida con bonificación de puntos
│   ├── game.py          # Controlador y bucle principal
│   ├── game_state.py    # Estados principales de la aplicación
│   ├── settings.py      # Configuración visual y general
│   ├── typing_stats.py  # Velocidad, precisión y errores
│   ├── wave_manager.py  # Oleadas y dificultad progresiva
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

Al ejecutar el proyecto aparecerá un enemigo que avanza hacia la base. Cada carácter
se marcará según coincida con su palabra y, al completar el objetivo, el enemigo será
reemplazado. Si alcanza la base, se perderá una vida. Al agotar las tres vidas puedes
reiniciar con `R`. Completar varias palabras seguidas aumenta el combo y el
multiplicador de puntos; perder una vida reinicia el combo. También puedes borrar con
Retroceso y pausar o reanudar con `Esc`. Desde el menú y la pantalla final, `Esc` cierra
el juego; el botón de la ventana permite cerrarlo en cualquier momento. Las PPM se
calculan desde la primera tecla escrita y la precisión compara cada intento con el
carácter esperado.
Cada cinco palabras completadas comienza una nueva oleada y aumenta la velocidad de
los enemigos hasta alcanzar el límite configurado. Desde la segunda oleada pueden
aparecer enemigos rápidos, que conceden el doble de puntos. Desde la tercera también
pueden aparecer blindados: son más lentos, pero necesitan dos palabras para caer.
