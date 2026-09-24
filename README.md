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
- Ventana redimensionable con escalado proporcional de la interfaz.
- HUD compacto con puntuación, oleada y vidas en la zona superior.
- Barra inferior con métricas, escritura, combo y cuatro potenciadores manuales.
- Arena ilustrada con una franja trasera de aparición aleatoria.
- Pantalla de inicio sobre un fondo limpio, navegable con teclado y ratón.
- Botones de juego, opciones, ayuda, salida, créditos y contacto.
- Selección de dificultad fácil, normal o difícil antes de cada partida.
- Menú de opciones controlable con teclado o ratón.
- Accesos a LinkedIn y GitHub desde Créditos y Contacto.
- Pantalla de ayuda con controles y reglas de enemigos.
- Modo de pantalla completa mediante la tecla F11.
- Música ambiental, efectos de combate y sonidos de escritura y borrado.
- Animaciones idle y de tecleo sincronizadas con la entrada del jugador.
- Reacciones de daño, muerte y reaparición con color y partículas.
- Control de volumen y silencio desde el menú de pausa.
- Cuenta atrás antes de empezar y después de reanudar la partida.
- Borrado continuo al mantener pulsada la tecla Retroceso.
- Palabras objetivo cargadas desde archivos externos y filtradas por tipo de enemigo.
- Varios enemigos simultáneos con posiciones aleatorias sobre el fondo de la plaza.
- Selección automática del objetivo mediante la primera letra escrita.
- Comparación visual de caracteres correctos e incorrectos.
- Selección automática de una nueva palabra al completar la actual.
- Enemigo móvil con velocidad independiente de los FPS.
- Enemigos normales, rápidos y blindados con comportamientos diferentes.
- Perspectiva suave y movimiento flotante para los enemigos voladores.
- Animaciones idle, de daño y de muerte para los siete tipos de enemigo.
- Rotura de escudo y ciclo de armadura dañada para el blindado.
- Daño y retirada inmediata cuando un enemigo alcanza al jugador.
- Contador de enemigos eliminados desglosado por tipo.
- Partículas y textos flotantes al atacar o recibir daño.
- Proyectiles dirigidos con animación de viaje e impacto sincronizado.
- Cuatro potenciadores manuales con cargas independientes y activación mediante `1` a `4`.
- Slow cubre la pantalla de nieve; x2 se activa al recogerlo y muestra una barra de tiempo.
- Shield rodea al jugador con una cúpula animada y estalla al bloquear daño; Pulso EMP expande ondas, reinicia y aturde a todos durante dos segundos.
- Multishot hace rebotar la siguiente bola por hasta dos objetivos adicionales.
- Recuperación automática con un corazón y flecha ascendente al ganar una vida.
- Récord persistente con puntuación, oleada, PPM y precisión.
- Eliminación del enemigo al completar su palabra.
- Sistema de tres vidas y registro de palabras completadas y falladas.
- Puntuación basada en la longitud, el tipo de enemigo y el combo.
- Combo de aciertos con multiplicador y barra animada que permanece llena y brillante en x5.
- Cálculo en tiempo real de PPM, precisión y errores de escritura.
- Oleadas con un 15 % más de velocidad por ronda y más enemigos simultáneos.
- Aviso animado, sonido y pausa de dos segundos entre oleadas.
- Pantalla de fin de partida con reinicio y reaparición visible mediante R.
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
│   ├── images/
│   │   ├── backgrounds/ # Fondos optimizados para el juego
│   │   ├── enemies/     # Animaciones separadas por tipo de enemigo
│   │   ├── effects/     # Proyectiles e impactos animados
│   │   └── player/      # Animaciones idle y de ataque del jugador
│   └── sounds/          # Música y efectos de sonido
├── data/
│   ├── words.txt        # Palabras generales
│   └── skeleton_words.txt # Palabras de tres letras
├── docs/
│   └── DEVELOPMENT_NOTES.md # Problemas resueltos y decisiones técnicas
├── game/
│   ├── __init__.py      # Define el paquete del juego
│   ├── audio_manager.py # Música, efectos, volumen y silencio
│   ├── armored_enemy.py # Variante resistente de dos palabras
│   ├── battlefield_renderer.py # Dibujo del campo de batalla
│   ├── difficulty.py    # Ajustes de las tres dificultades
│   ├── enemy.py         # Movimiento y representación del enemigo
│   ├── enemy_manager.py # Aparición, movimiento y selección de objetivos
│   ├── enemy_type.py    # Identificadores de las variantes enemigas
│   ├── boss_enemy.py        # Golem invocador de las rondas 5, 10, 15...
│   ├── necromancer_enemy.py # Invocador inmóvil de esqueletos
│   ├── skeleton_enemy.py # Enemigo invocado con palabra corta
│   ├── effects.py       # Partículas y mensajes visuales temporales
│   ├── fast_enemy.py    # Variante rápida con bonificación de puntos
│   ├── game.py          # Controlador y bucle principal
│   ├── game_state.py    # Estados principales de la aplicación
│   ├── goblin_enemy.py # Cinco desvíos antes de tocar al jugador
│   ├── power_up_manager.py # Cargas y efectos temporales de power-ups
│   ├── power_up_type.py # Identificadores, ranuras y colores de power-ups
│   ├── player_renderer.py # Carga y animación visual del jugador
│   ├── enemy_renderer.py # Carga, escala y dibujo de enemigos
│   ├── projectile_manager.py # Proyectiles dirigidos e impactos
│   ├── save_manager.py  # Guardado local del mejor resultado
│   ├── settings.py      # Configuración visual y general
│   ├── typing_stats.py  # Velocidad, precisión y errores
│   ├── ui_renderer.py   # HUD, campo de escritura y pantallas superpuestas
│   ├── wave_manager.py  # Oleadas y dificultad progresiva
│   └── word_manager.py  # Carga y selección de palabras
├── .gitignore           # Archivos excluidos del repositorio
├── main.py              # Punto de entrada
├── README.md            # Documentación
└── requirements.txt     # Dependencias de Python
```

Los archivos `.gitkeep` permiten conservar en Git las carpetas que todavía están vacías.

## Notas de desarrollo

Los problemas técnicos más relevantes y sus soluciones se documentan en
[`docs/DEVELOPMENT_NOTES.md`](docs/DEVELOPMENT_NOTES.md). Estas notas explican
el razonamiento seguido y las comprobaciones realizadas durante el desarrollo.

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

La pantalla inicial permite jugar, configurar el audio y la pantalla completa,
consultar la ayuda, abrir Créditos y Contacto o salir. Todos sus accesos se pueden
recorrer con las flechas. Al pulsar Jugar se elige entre dificultad fácil, normal
o difícil; cada nivel modifica la velocidad y la frecuencia de aparición. Tras
confirmarla, el jugador reaparece mediante una animación antes de comenzar.
Al comenzar aparecerán enemigos en puntos aleatorios de la franja trasera de la
plaza y avanzarán directamente hacia el jugador, manteniendo libre el primer plano.
El prefijo escrito permite distinguir a los enemigos que comparten inicial;
cada carácter se marcará según sea correcto o incorrecto. Si un enemigo
alcanza la base, se perderá una vida. Al agotar las tres vidas puedes
reiniciar con `R`. Completar varias palabras seguidas aumenta el combo y el
multiplicador de puntos; perder una vida reinicia el combo. También puedes borrar con
Retroceso y activar los cuatro potenciadores manuales con `1` a `4`:
Ralentización, Shield, Pulso EMP y Multishot. Recuperación y Puntuación doble
se activan al obtenerse, con un aviso sonoro. Recuperación restaura una vida roja;
si las tres están completas, añade un corazón verde que desaparece al absorber
daño. `Esc` pausa o reanuda. Durante la pausa, las flechas izquierda y derecha
ajustan el volumen y
`M` activa o desactiva el silencio. La tecla `H` abre la ayuda desde el menú,
la pausa o la pantalla final y `F11` alterna el modo de pantalla completa.
Desde el menú y la pantalla final, `Esc` cierra
el juego; el botón de la ventana permite cerrarlo en cualquier momento. Las PPM se
calculan desde la primera tecla escrita y la precisión compara cada intento con el
carácter esperado.
Las oleadas no tienen límite y avanzan por enemigos derrotados: la primera
requiere cinco bajas y cada oleada normal suma tres. El Gobling y el normal
aparecen desde el principio; el blindado desde la tercera, el rápido desde la
séptima y el nigromante desde la undécima. Cada quinta oleada presenta un
golem inmóvil con resistencia creciente. Cada 1,5 segundos invoca un enemigo
aleatorio entre los tipos desbloqueados, salvo el esqueleto. El nigromante puede
ser invocado por el jefe desde la ronda 10; en la ronda 5 no aparece.
La ronda termina solo al derrotar al jefe. Al cambiar de oleada, suena un aviso, se limpia la arena y
transcurren dos segundos antes de que aparezcan nuevos enemigos. La velocidad
base de los enemigos parte de un valor más bajo y aumenta un 15 % por oleada.
El jefe usa palabras de exactamente siete letras en la ronda 5, ocho en la 10,
nueve en la 15 y suma una letra en cada aparición. Para rondas extremas sin
palabras de esa longitud, combina términos del vocabulario en una secuencia
sin espacios de la longitud exacta. Los esqueletos invocados no cuentan para
completar la oleada, aunque conceden algunos puntos y pueden cargar un potenciador con
menor probabilidad. El Gobling se desvía cinco veces mientras se acerca al
jugador; el nigromante permanece en su punto de aparición e invoca esqueletos
con palabras de tres letras. Si varias palabras comparten inicial, el
jugador puede seguir escribiendo hasta que el prefijo identifique su objetivo.

Los normales, Goblings y blindados usan palabras de hasta cinco letras; los rápidos,
de hasta cuatro; los nigromantes, de más de cinco; y los esqueletos, de tres.
El blindado muestra desde el principio la palabra de su segundo golpe y permite
escribirla en cuanto sale el primer disparo, sin esperar al impacto.
