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
LANE_COLOR = (195, 88, 24)
ENEMY_COLOR = (235, 55, 65)
ENEMY_OUTLINE_COLOR = (105, 28, 35)
ENEMY_CORE_COLOR = (255, 175, 180)
FAST_ENEMY_COLOR = (255, 185, 35)
FAST_ENEMY_OUTLINE_COLOR = (125, 75, 20)
FAST_ENEMY_CORE_COLOR = (255, 235, 155)
ARMORED_ENEMY_COLOR = (55, 115, 235)
ARMORED_ENEMY_OUTLINE_COLOR = (25, 55, 125)
ARMORED_ENEMY_CORE_COLOR = (175, 205, 255)
PLAYER_COLOR = (80, 220, 180)
PLAYER_OUTLINE_COLOR = (35, 105, 90)
GAME_OVER_OVERLAY_COLOR = (8, 10, 18, 225)


# Tamaños de las fuentes utilizadas en la interfaz.
TITLE_FONT_SIZE = 64
TARGET_FONT_SIZE = 38
BODY_FONT_SIZE = 32
SMALL_FONT_SIZE = 22


# Dimensiones y límites de la zona de escritura.
INPUT_BOX_WIDTH = 680
INPUT_BOX_HEIGHT = 64
INPUT_BOX_CENTER_Y = 660
MAX_INPUT_LENGTH = 32

# Configuración de repetición para teclas mantenidas.
# El retardo indica cuánto tarda en comenzar la repetición.
KEY_REPEAT_DELAY = 350

# El intervalo determina los milisegundos entre repeticiones.
KEY_REPEAT_INTERVAL = 45

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
ENEMY_SPEED = 80.0
ENEMY_REACH_DISTANCE = 8.0
STARTING_LIVES = 3

# La dificultad aumenta al completar grupos de palabras.
WORDS_PER_WAVE = 5
ENEMY_SPEED_INCREMENT = 20.0
MAX_ENEMY_SPEED = 200.0

# Ritmo y cantidad de enemigos presentes al mismo tiempo.
BASE_ENEMY_SPAWN_INTERVAL = 3.0
MIN_ENEMY_SPAWN_INTERVAL = 1.25
SPAWN_INTERVAL_DECREASE = 0.15
BASE_MAX_ENEMIES = 2
WAVES_PER_ENEMY_SLOT = 2
MAX_SIMULTANEOUS_ENEMIES = 5

# Los enemigos rápidos aparecen gradualmente desde la segunda oleada.
FAST_ENEMY_FIRST_WAVE = 2
FAST_ENEMY_BASE_CHANCE = 0.35
FAST_ENEMY_CHANCE_INCREMENT = 0.05
MAX_FAST_ENEMY_CHANCE = 0.60
FAST_ENEMY_SPEED_MULTIPLIER = 1.50
FAST_ENEMY_SCORE_MULTIPLIER = 2

# Los blindados son lentos, resistentes y aparecen desde la tercera oleada.
ARMORED_ENEMY_FIRST_WAVE = 3
ARMORED_ENEMY_BASE_CHANCE = 0.20
ARMORED_ENEMY_CHANCE_INCREMENT = 0.03
MAX_ARMORED_ENEMY_CHANCE = 0.30
ARMORED_ENEMY_SPEED_MULTIPLIER = 0.70
ARMORED_ENEMY_SCORE_MULTIPLIER = 2
ARMORED_ENEMY_HEALTH = 2

# Configuración del sistema de puntuación y combos.
# Cada letra aporta puntos y el multiplicador sube cada tres aciertos seguidos.
POINTS_PER_CHARACTER = 10
WORDS_PER_MULTIPLIER_LEVEL = 3
MAX_COMBO_MULTIPLIER = 5
COMBO_BAR_WIDTH = 520
COMBO_BAR_HEIGHT = 12
COMBO_BAR_CENTER_Y = 611

# Paneles laterales que mantienen el centro despejado para el combate.
HUD_PANEL_MARGIN = 20
WAVE_PANEL_TOP = 20
WAVE_PANEL_WIDTH = 260
WAVE_PANEL_HEIGHT = 78
STATS_PANEL_TOP = 500
STATS_PANEL_WIDTH = 260
STATS_PANEL_HEIGHT = 205
POWER_UP_PANEL_TOP = 500
POWER_UP_PANEL_WIDTH = 260
POWER_UP_PANEL_HEIGHT = 205
POWER_UP_SLOT_SIZE = 68

# La ralentización puede guardarse y activarse cuando el jugador la necesite.
SLOW_POWER_UP_DROP_CHANCE = 0.25
SLOW_POWER_UP_DURATION = 5.0
SLOW_ENEMY_SPEED_MULTIPLIER = 0.45

# Los carriles se abren en abanico desde el jugador hacia la parte superior.
# El orden alterna centro, izquierda y derecha para repartir las apariciones.
ENEMY_LANE_START_POSITIONS = (
    (640.0, 190.0),
    (390.0, 135.0),
    (890.0, 135.0),
    (160.0, 155.0),
    (1120.0, 155.0),
    (40.0, 185.0),
    (1240.0, 185.0),
)
PLAYER_POSITION = (WINDOW_WIDTH / 2, 565.0)
PLAYER_RADIUS = 32
