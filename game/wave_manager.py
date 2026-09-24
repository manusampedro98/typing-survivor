"""Progresión sin límite basada en enemigos derrotados."""

from game.difficulty import Difficulty
from game.settings import (
    ARMORED_ENEMY_FIRST_WAVE,
    BASE_ENEMY_SPAWN_INTERVAL,
    BASE_MAX_ENEMIES,
    BOSS_WAVE_INTERVAL,
    ENEMY_SPEED,
    FAST_ENEMY_FIRST_WAVE,
    FIRST_WAVE_KILLS,
    KILLS_ADDED_PER_WAVE,
    MAX_SIMULTANEOUS_ENEMIES,
    MIN_ENEMY_SPAWN_INTERVAL,
    SPAWN_INTERVAL_DECREASE,
    WAVES_PER_ENEMY_SLOT,
)


class WaveManager:
    """Cuenta las bajas válidas y configura el ritmo de cada oleada."""

    def __init__(self) -> None:
        self.current_wave = 1
        self.defeated_in_wave = 0
        self.difficulty = Difficulty.NORMAL

    def set_difficulty(self, difficulty: Difficulty) -> None:
        self.difficulty = difficulty

    @property
    def is_boss_wave(self) -> bool:
        return self.current_wave % BOSS_WAVE_INTERVAL == 0

    @property
    def required_kills(self) -> int:
        if self.is_boss_wave:
            return 1
        return FIRST_WAVE_KILLS + (self.current_wave - 1) * KILLS_ADDED_PER_WAVE

    @property
    def enemy_speed(self) -> float:
        speed = ENEMY_SPEED * self.difficulty.speed_growth ** (self.current_wave - 1)
        return speed * self.difficulty.speed_multiplier

    @property
    def enemy_spawn_interval(self) -> float:
        interval = BASE_ENEMY_SPAWN_INTERVAL - (
            self.current_wave - 1
        ) * SPAWN_INTERVAL_DECREASE
        return max(interval, MIN_ENEMY_SPAWN_INTERVAL) * self.difficulty.spawn_interval_multiplier

    @property
    def max_simultaneous_enemies(self) -> int:
        if self.is_boss_wave:
            return 1
        additional_slots = (self.current_wave - 1) // WAVES_PER_ENEMY_SLOT
        extra_slots = self.difficulty.extra_enemy_slots
        return min(
            BASE_MAX_ENEMIES + additional_slots + extra_slots,
            MAX_SIMULTANEOUS_ENEMIES + extra_slots,
        )

    def register_defeat(
        self, is_skeleton: bool = False, is_boss: bool = False
    ) -> bool:
        """El jefe solo termina su ronda; los esqueletos no aportan bajas."""
        if self.is_boss_wave and not is_boss:
            return False
        if is_skeleton or self.defeated_in_wave >= self.required_kills:
            return False
        self.defeated_in_wave += 1
        return self.defeated_in_wave == self.required_kills

    def advance_wave(self) -> None:
        """Prepara la siguiente oleada después de limpiar la arena."""
        self.current_wave += 1
        self.defeated_in_wave = 0

    def reset(self) -> None:
        self.current_wave = 1
        self.defeated_in_wave = 0
