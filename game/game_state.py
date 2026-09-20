"""Estados disponibles durante la ejecución del juego."""

from enum import Enum, auto


class GameState(Enum):
    """Representa las pantallas y modos principales de la aplicación."""

    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
