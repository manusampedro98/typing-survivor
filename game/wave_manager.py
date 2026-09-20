"""Progresión de oleadas y dificultad de la partida."""

from game.settings import (
    ARMORED_ENEMY_BASE_CHANCE,
    ARMORED_ENEMY_CHANCE_INCREMENT,
    ARMORED_ENEMY_FIRST_WAVE,
    BASE_ENEMY_SPAWN_INTERVAL,
    BASE_MAX_ENEMIES,
    ENEMY_SPEED,
    ENEMY_SPEED_INCREMENT,
    FAST_ENEMY_BASE_CHANCE,
    FAST_ENEMY_CHANCE_INCREMENT,
    FAST_ENEMY_FIRST_WAVE,
    MAX_ARMORED_ENEMY_CHANCE,
    MAX_ENEMY_SPEED,
    MAX_FAST_ENEMY_CHANCE,
    MAX_SIMULTANEOUS_ENEMIES,
    MIN_ENEMY_SPAWN_INTERVAL,
    SPAWN_INTERVAL_DECREASE,
    WAVES_PER_ENEMY_SLOT,
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

    @property
    def armored_enemy_chance(self) -> float:
        """Calcula la probabilidad de generar un enemigo blindado."""

        if self.current_wave < ARMORED_ENEMY_FIRST_WAVE:
            return 0.0

        additional_chance = (
            self.current_wave - ARMORED_ENEMY_FIRST_WAVE
        ) * ARMORED_ENEMY_CHANCE_INCREMENT
        return min(
            ARMORED_ENEMY_BASE_CHANCE + additional_chance,
            MAX_ARMORED_ENEMY_CHANCE,
        )

    @property
    def enemy_spawn_interval(self) -> float:
        """Devuelve el tiempo entre apariciones para la oleada actual."""

        interval = BASE_ENEMY_SPAWN_INTERVAL - (
            self.current_wave - 1
        ) * SPAWN_INTERVAL_DECREASE
        return max(interval, MIN_ENEMY_SPAWN_INTERVAL)

    @property
    def max_simultaneous_enemies(self) -> int:
        """Calcula cuántos enemigos pueden coincidir en pantalla."""

        additional_slots = (
            self.current_wave - 1
        ) // WAVES_PER_ENEMY_SLOT
        return min(
            BASE_MAX_ENEMIES + additional_slots,
            MAX_SIMULTANEOUS_ENEMIES,
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
