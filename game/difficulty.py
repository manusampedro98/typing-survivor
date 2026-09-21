"""Niveles de dificultad disponibles antes de comenzar una partida."""

from enum import Enum


class Difficulty(Enum):
    """Agrupa el ritmo y la frecuencia de aparición de los enemigos."""

    EASY = (
        "FÁCIL",
        "Enemigos más lentos y con más tiempo entre apariciones.",
        0.85,
        1.18,
    )
    NORMAL = (
        "NORMAL",
        "La experiencia equilibrada de Typing Survivor.",
        1.0,
        1.0,
    )
    HARD = (
        "DIFÍCIL",
        "Enemigos más rápidos y oleadas con mayor presión.",
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
