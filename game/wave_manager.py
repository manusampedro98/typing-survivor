"""Progresión de oleadas y dificultad de la partida."""

from game.settings import (
    ENEMY_SPEED,
    ENEMY_SPEED_INCREMENT,
    FAST_ENEMY_BASE_CHANCE,
    FAST_ENEMY_CHANCE_INCREMENT,
    FAST_ENEMY_FIRST_WAVE,
    MAX_ENEMY_SPEED,
    MAX_FAST_ENEMY_CHANCE,
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

    @property
    def fast_enemy_chance(self) -> float:
        """Calcula la probabilidad de generar un enemigo rápido."""

        if self.current_wave < FAST_ENEMY_FIRST_WAVE:
            return 0.0

        additional_chance = (
            self.current_wave - FAST_ENEMY_FIRST_WAVE
        ) * FAST_ENEMY_CHANCE_INCREMENT
        return min(
            FAST_ENEMY_BASE_CHANCE + additional_chance,
            MAX_FAST_ENEMY_CHANCE,
        )

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
