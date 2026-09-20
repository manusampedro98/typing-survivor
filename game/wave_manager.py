"""Progresión de oleadas y dificultad de la partida."""

from game.settings import (
    ENEMY_SPEED,
    ENEMY_SPEED_INCREMENT,
    MAX_ENEMY_SPEED,
    WORDS_PER_WAVE,
)


class WaveManager:
    """Controla la oleada actual y la velocidad de los enemigos."""

    def __init__(self) -> None:
        """Comienza la progresión desde la primera oleada."""

        self.current_wave = 1
        self.completed_words_in_wave = 0

    @property
    def enemy_speed(self) -> float:
        """Calcula la velocidad correspondiente a la oleada actual."""

        speed = ENEMY_SPEED + (
            self.current_wave - 1
        ) * ENEMY_SPEED_INCREMENT
        return min(speed, MAX_ENEMY_SPEED)

    def register_completed_word(self) -> None:
        """Avanza de oleada al alcanzar el número de palabras requerido."""

        self.completed_words_in_wave += 1

        if self.completed_words_in_wave >= WORDS_PER_WAVE:
            self.current_wave += 1
            self.completed_words_in_wave = 0

    def reset(self) -> None:
        """Restablece la progresión para comenzar una partida nueva."""

        self.current_wave = 1
        self.completed_words_in_wave = 0
