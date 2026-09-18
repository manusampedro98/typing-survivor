"""Configuración compartida de Typing Survivor."""


# Dimensiones de la ventana principal en píxeles.
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Texto mostrado en la barra superior de la ventana.
WINDOW_TITLE = "Typing Survivor"

# Número máximo de fotogramas procesados por segundo.
FPS = 60


# Paleta principal de la interfaz en formato RGB.
BACKGROUND_COLOR = (16, 18, 27)
PANEL_COLOR = (25, 29, 42)
BORDER_COLOR = (57, 65, 86)
TEXT_COLOR = (237, 240, 247)
MUTED_TEXT_COLOR = (150, 158, 180)
ACCENT_COLOR = (65, 202, 255)
CORRECT_COLOR = (80, 220, 140)
INCORRECT_COLOR = (255, 95, 110)


# Tamaños de las fuentes utilizadas en la interfaz.
TITLE_FONT_SIZE = 64
TARGET_FONT_SIZE = 52
BODY_FONT_SIZE = 32
SMALL_FONT_SIZE = 22


# Dimensiones y límites de la zona de escritura.
INPUT_BOX_WIDTH = 680
INPUT_BOX_HEIGHT = 80
MAX_INPUT_LENGTH = 32

# Configuración de repetición para teclas mantenidas.
# El retardo indica cuánto tarda en comenzar la repetición.
KEY_REPEAT_DELAY = 350

# El intervalo determina los milisegundos entre repeticiones.
KEY_REPEAT_INTERVAL = 45

# Separación horizontal entre el texto y el borde del panel.
INPUT_HORIZONTAL_PADDING = 24

# Configuración visual y temporal del cursor de escritura.
CARET_WIDTH = 3
CARET_HEIGHT = 36
CARET_BLINK_INTERVAL = 500
