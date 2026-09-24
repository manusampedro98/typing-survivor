"""Golem inmóvil que dirige las oleadas de jefe."""

from game.armored_enemy import ArmoredEnemy
from game.enemy_type import EnemyType
from game.settings import (
    BOSS_BASE_HEALTH,
    BOSS_ENEMY_COLOR,
    BOSS_HEALTH_PER_APPEARANCE,
    BOSS_SCORE_MULTIPLIER,
    BOSS_SUMMON_INTERVAL,
    BOSS_WAVE_INTERVAL,
    ENEMY_SPEED,
)


class BossEnemy(ArmoredEnemy):
    """Resiste varias palabras e invoca un refuerzo cada 1,5 segundos."""

    def __init__(
        self,
        word: str,
        start_position: tuple[float, float],
        target_position: tuple[float, float],
        speed: float = ENEMY_SPEED,
        wave_number: int = BOSS_WAVE_INTERVAL,
    ) -> None:
        super().__init__(word, start_position, target_position, speed)
        self.enemy_type = EnemyType.BOSS
        self.label_color = BOSS_ENEMY_COLOR
        self.max_health = BOSS_BASE_HEALTH + (
            wave_number // BOSS_WAVE_INTERVAL - 1
        ) * BOSS_HEALTH_PER_APPEARANCE
        self.health = self.max_health
        self.speed = 0.0
        self.score_multiplier = BOSS_SCORE_MULTIPLIER
        self.summon_elapsed = 0.0

    def update(self, delta_time: float) -> None:
        """Prepara la siguiente invocación sin mover al golem."""
        self.summon_elapsed = min(
            BOSS_SUMMON_INTERVAL,
            self.summon_elapsed + max(0.0, delta_time),
        )

    @property
    def ready_to_summon(self) -> bool:
        return self.summon_elapsed >= BOSS_SUMMON_INTERVAL

    def mark_summoned(self) -> None:
        self.summon_elapsed = 0.0
