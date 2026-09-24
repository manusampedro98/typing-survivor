"""Niveles de dificultad disponibles antes de comenzar una partida."""

from enum import Enum

from game.settings import ENEMY_SPEED_GROWTH


class Difficulty(Enum):
    """Agrupa el ritmo y la frecuencia de aparición de los enemigos."""

    EASY = (
        "FÁCIL",
        "Más enemigos en pantalla, mitad de velocidad y +5 % por oleada.",
        0.5,
        0.8,
    )
    NORMAL = (
        "NORMAL",
        "Ritmo habitual y +15 % de velocidad por oleada.",
        1.0,
        1.0,
    )
    HARD = (
        "DIFÍCIL",
        "Más presión y +30 % de velocidad por oleada.",
        1.18,
        0.84,
    )

    def __init__(
        self,
        display_name: str,
        description: str,
        speed_multiplier: float,
        spawn_interval_multiplier: float,
    ) -> None:
        self.display_name = display_name
        self.description = description
        self.speed_multiplier = speed_multiplier
        self.spawn_interval_multiplier = spawn_interval_multiplier

    @property
    def speed_growth(self) -> float:
        """Factor de velocidad aplicado en cada nueva oleada."""

        if self is Difficulty.EASY:
            return 1.05
        if self is Difficulty.HARD:
            return 1.30
        return ENEMY_SPEED_GROWTH

    @property
    def extra_enemy_slots(self) -> int:
        """Plazas simultáneas adicionales sin alargar la oleada."""

        return 2 if self is Difficulty.EASY else 0
