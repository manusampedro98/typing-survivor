"""Configuración compartida de Typing Survivor."""


# Dimensiones de la ventana principal en píxeles.
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 450

# Texto mostrado en la barra superior de la ventana.
WINDOW_TITLE = "Typing Survivor"

# Número máximo de fotogramas procesados por segundo.
FPS = 60

# Tiempo de preparación antes de iniciar o reanudar la acción.
COUNTDOWN_DURATION = 3.0

# El volumen se controla desde la pausa en pasos del diez por ciento.
DEFAULT_AUDIO_VOLUME = 0.6
AUDIO_VOLUME_STEP = 0.1
MUSIC_VOLUME_MULTIPLIER = 0.35


# Paleta principal de la interfaz en formato RGB.
BACKGROUND_COLOR = (16, 18, 27)
PANEL_COLOR = (25, 29, 42)
BORDER_COLOR = (57, 65, 86)
TEXT_COLOR = (237, 240, 247)
MUTED_TEXT_COLOR = (150, 158, 180)
ACCENT_COLOR = (65, 202, 255)
CORRECT_COLOR = (80, 220, 140)
INCORRECT_COLOR = (255, 95, 110)
POWER_UP_COLOR = (180, 110, 255)
ENEMY_COLOR = (235, 55, 65)
ENEMY_OUTLINE_COLOR = (105, 28, 35)
ENEMY_CORE_COLOR = (255, 175, 180)
FAST_ENEMY_COLOR = (255, 185, 35)
FAST_ENEMY_OUTLINE_COLOR = (125, 75, 20)
FAST_ENEMY_CORE_COLOR = (255, 235, 155)
ARMORED_ENEMY_COLOR = (55, 115, 235)
ARMORED_ENEMY_OUTLINE_COLOR = (25, 55, 125)
ARMORED_ENEMY_CORE_COLOR = (175, 205, 255)
BOSS_ENEMY_COLOR = (190, 110, 255)
GOBLIN_ENEMY_COLOR = (165, 210, 68)
GOBLIN_ENEMY_OUTLINE_COLOR = (67, 94, 29)
GOBLIN_ENEMY_CORE_COLOR = (224, 245, 150)
NECROMANCER_ENEMY_COLOR = (186, 100, 235)
NECROMANCER_ENEMY_OUTLINE_COLOR = (80, 43, 111)
NECROMANCER_ENEMY_CORE_COLOR = (227, 183, 255)
SKELETON_ENEMY_COLOR = (223, 217, 192)
SKELETON_ENEMY_OUTLINE_COLOR = (91, 84, 100)
SKELETON_ENEMY_CORE_COLOR = (246, 240, 216)
PLAYER_COLOR = (80, 220, 180)
PLAYER_OUTLINE_COLOR = (35, 105, 90)
GAME_OVER_OVERLAY_COLOR = (8, 10, 18, 225)
RESTART_OVERLAY_ALPHA = 105

# Una capa tenue mantiene legibles las entidades sobre el fondo ilustrado.
ARENA_BACKGROUND_DARKEN_ALPHA = 42


# Tamaños de las fuentes utilizadas en la interfaz.
TITLE_FONT_SIZE = 64
TARGET_FONT_SIZE = 38
BODY_FONT_SIZE = 32
SMALL_FONT_SIZE = 22


# Dimensiones y posición del campo de escritura dentro del HUD inferior.
INPUT_BOX_WIDTH = 430
INPUT_BOX_HEIGHT = 58
INPUT_BOX_CENTER_X = 625
INPUT_BOX_CENTER_Y = 640
MAX_INPUT_LENGTH = 32

# Configuración de repetición para teclas mantenidas.
# El retardo indica cuánto tarda en comenzar la repetición.
KEY_REPEAT_DELAY = 350

# El intervalo determina los milisegundos entre repeticiones.
KEY_REPEAT_INTERVAL = 45

# El borrado repetido limita el audio para evitar solapar demasiados efectos.
BACKSPACE_SOUND_INTERVAL = 90

# Tiempo durante el que se ignora una tecla usada como control del juego.
CONTROL_INPUT_BLOCK_DURATION = 150

# Separación horizontal entre el texto y el borde del panel.
INPUT_HORIZONTAL_PADDING = 24

# Configuración visual y temporal del cursor de escritura.
CARET_WIDTH = 3
CARET_HEIGHT = 36
CARET_BLINK_INTERVAL = 500


# Configuración del enemigo provisional.
ENEMY_RADIUS = 28
ENEMY_SPEED = 65.0
ENEMY_REACH_DISTANCE = 8.0
STARTING_LIVES = 3

# Las oleadas normales exigen cinco bajas iniciales y tres más por ronda.
FIRST_WAVE_KILLS = 5
KILLS_ADDED_PER_WAVE = 3
BOSS_WAVE_INTERVAL = 5
WAVE_BREAK_DURATION = 2.0
ENEMY_SPEED_GROWTH = 1.15

# Ritmo y cantidad de enemigos presentes al mismo tiempo.
BASE_ENEMY_SPAWN_INTERVAL = 2.4
MIN_ENEMY_SPAWN_INTERVAL = 1.5
SPAWN_INTERVAL_DECREASE = 0.05
BASE_MAX_ENEMIES = 3
WAVES_PER_ENEMY_SLOT = 2
MAX_SIMULTANEOUS_ENEMIES = 8

# Los enemigos rápidos se incorporan desde la séptima oleada.
FAST_ENEMY_FIRST_WAVE = 7
FAST_ENEMY_BASE_CHANCE = 0.35
FAST_ENEMY_CHANCE_INCREMENT = 0.05
MAX_FAST_ENEMY_CHANCE = 0.60
FAST_ENEMY_SPEED_MULTIPLIER = 1.50
FAST_ENEMY_SCORE_MULTIPLIER = 3

# Los blindados son lentos, resistentes y aparecen desde la tercera oleada.
ARMORED_ENEMY_FIRST_WAVE = 3
ARMORED_ENEMY_BASE_CHANCE = 0.20
ARMORED_ENEMY_CHANCE_INCREMENT = 0.03
MAX_ARMORED_ENEMY_CHANCE = 0.30
ARMORED_ENEMY_SPEED_MULTIPLIER = 0.70
ARMORED_ENEMY_SCORE_MULTIPLIER = 2
ARMORED_ENEMY_HEALTH = 2

GOBLIN_ENEMY_FIRST_WAVE = 1
NECROMANCER_ENEMY_FIRST_WAVE = 11
NECROMANCER_SCORE_MULTIPLIER = 5

# El golem permanece inmóvil e invoca refuerzos durante el combate.
BOSS_WORD_START_LENGTH = 7
BOSS_BASE_HEALTH = 3
BOSS_HEALTH_PER_APPEARANCE = 1
BOSS_SCORE_MULTIPLIER = 10
BOSS_VISIBLE_SIZE = 185
BOSS_SUMMON_INTERVAL = 1.5
BOSS_IDLE_FPS = 5.0
BOSS_DAMAGE_FPS = 12.0
BOSS_SUMMON_FPS = 12.0
BOSS_DEATH_FPS = 8.0

# El goblin cambia de rumbo cinco veces antes del último avance.
GOBLIN_RANDOM_MOVES = 5
GOBLIN_WANDER_ANGLE = 32.0
GOBLIN_MAX_TURN_ANGLE = 25.0
GOBLIN_WAYPOINT_ATTEMPTS = 20

# El nigromante permanece inmóvil y mantiene hasta tres invocaciones.
NECROMANCER_SUMMON_INTERVAL = 4.0
NECROMANCER_MAX_SKELETONS = 3
NECROMANCER_SUMMON_OFFSETS = ((-78.0, 54.0), (78.0, 54.0), (0.0, 85.0))
NECROMANCER_VISIBLE_SIZE = 84
SKELETON_SPEED_MULTIPLIER = 1.10

# La dimensión visible mayor de cada enemigo alcanza la altura visible del
# jugador al final del recorrido. Al aparecer conserva profundidad sin ser diminuto.
ENEMY_ARRIVAL_SIZE = 110
MIN_ENEMY_PERSPECTIVE_SCALE = 0.55

# Una oscilación vertical y una inclinación leve hacen volar al enemigo rápido.
FAST_ENEMY_FLIGHT_BOB_HEIGHT = 7.0
FAST_ENEMY_FLIGHT_SPEED = 3.4
FAST_ENEMY_FLIGHT_ROLL = 2.5

# Ritmo de las secuencias del enemigo normal.
NORMAL_ENEMY_IDLE_FPS = 4.0
NORMAL_ENEMY_DAMAGE_FPS = 12.0
NORMAL_ENEMY_DEATH_FPS = 8.0

# El aleteo y la caída del murciélago utilizan un ritmo algo más rápido.
FAST_ENEMY_IDLE_FPS = 9.0
FAST_ENEMY_DAMAGE_FPS = 12.0
FAST_ENEMY_DEATH_FPS = 10.0

# El blindado cambia de ciclo al perder el escudo en el primer impacto.
ARMORED_ENEMY_IDLE_FPS = 5.0
ARMORED_ENEMY_SHIELD_BREAK_FPS = 12.0
ARMORED_ENEMY_DEATH_FPS = 8.0

GOBLIN_ENEMY_IDLE_FPS = 6.0
GOBLIN_ENEMY_DAMAGE_FPS = 12.0
GOBLIN_ENEMY_DEATH_FPS = 8.0

NECROMANCER_ENEMY_IDLE_FPS = 5.0
NECROMANCER_ENEMY_DAMAGE_FPS = 12.0
NECROMANCER_ENEMY_SUMMON_FPS = 12.0
NECROMANCER_ENEMY_DEATH_FPS = 8.0
SKELETON_ENEMY_IDLE_FPS = 7.0
SKELETON_ENEMY_DAMAGE_FPS = 12.0
SKELETON_ENEMY_DEATH_FPS = 9.0

# Configuración del sistema de puntuación y combos.
# Cada letra aporta puntos y el multiplicador sube cada tres aciertos seguidos.
POINTS_PER_CHARACTER = 10
WORDS_PER_MULTIPLIER_LEVEL = 3
MAX_COMBO_MULTIPLIER = 5
COMBO_BAR_WIDTH = INPUT_BOX_WIDTH
COMBO_BAR_HEIGHT = 12

# El HUD agrupa la información principal arriba y los controles abajo.
HUD_PANEL_MARGIN = 20
TOP_HUD_TOP = 20
TOP_HUD_HEIGHT = 64
BOTTOM_HUD_TOP = 590
BOTTOM_HUD_HEIGHT = 100
POWER_UP_SLOT_SIZE = 50
POWER_UP_SLOT_GAP = 8

# Los enemigos pueden entregar una habilidad manual o automática.
POWER_UP_DROP_CHANCE = 0.25
SKELETON_SCORE_MULTIPLIER = 0.5
SKELETON_POWER_UP_CHANCE_MULTIPLIER = 0.4
SLOW_POWER_UP_DURATION = 5.0
SLOW_ENEMY_SPEED_MULTIPLIER = 0.45
EMP_STUN_DURATION = 2.0
MULTISHOT_CHAIN_TARGETS = 2
DOUBLE_POINTS_DURATION = 8.0

# La ruta de aparición sigue visualmente el límite trasero de la plaza.
# Una variación vertical pequeña evita que los enemigos formen una fila rígida.
ENEMY_SPAWN_PATH_POINTS = (
    (105.0, 260.0),
    (190.0, 205.0),
    (300.0, 185.0),
    (440.0, 188.0),
    (600.0, 195.0),
    (760.0, 207.0),
    (900.0, 220.0),
    (1040.0, 240.0),
    (1135.0, 268.0),
)
ENEMY_SPAWN_VERTICAL_JITTER = 10.0
ENEMY_SPAWN_MIN_SEPARATION = 125.0
ENEMY_SPAWN_POSITION_ATTEMPTS = 64
PLAYER_POSITION = (WINDOW_WIDTH / 2, 545.0)
PLAYER_RADIUS = 32

# El lienzo transparente mantiene todos los fotogramas alineados. La base del
# sprite queda justo encima del HUD inferior sin cambiar el punto de colisión.
PLAYER_SPRITE_SIZE = (150, 150)
PLAYER_SPRITE_BOTTOM_Y = BOTTOM_HUD_TOP
PLAYER_IDLE_FPS = 6.0
PLAYER_ATTACK_FPS = 12.0
PLAYER_DAMAGE_FPS = 12.0
PLAYER_DEATH_FPS = 8.0
PLAYER_REVIVE_FPS = 10.0

# Cada pulsación prolonga brevemente el ciclo de tecleo. Al dejar de escribir,
# el personaje vuelve automáticamente a la animación idle.
PLAYER_TYPING_HOLD_DURATION = 0.5

# El proyectil nace sobre el teclado y utiliza recursos cuadrados para poder
# viajar por cualquier trayectoria sin necesitar rotaciones adicionales.
PLAYER_PROJECTILE_ORIGIN = (674.0, 518.0)
ENERGY_PROJECTILE_SPEED = 900.0
ENERGY_BALL_SIZE = (56, 56)
ENERGY_BALL_FPS = 14.0
ENERGY_IMPACT_SIZE = (128, 128)
ENERGY_IMPACT_FPS = 15.0
