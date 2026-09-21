"""Estados disponibles durante la ejecución del juego."""

from enum import Enum, auto


class GameState(Enum):
    """Representa las pantallas y modos principales de la aplicación."""

    MENU = auto()
    DIFFICULTY = auto()
    OPTIONS = auto()
    CREDITS = auto()
    CONTACT = auto()
    COUNTDOWN = auto()
    PLAYING = auto()
    DYING = auto()
    PAUSED = auto()
    HELP = auto()
    GAME_OVER = auto()
