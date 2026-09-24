"""Nigromante inmóvil que invoca esqueletos desde el fondo."""

import pygame

from game.enemy import Enemy
from game.enemy_type import EnemyType
from game.settings import (
    ENEMY_SPEED,
    NECROMANCER_ENEMY_COLOR,
    NECROMANCER_ENEMY_CORE_COLOR,
    NECROMANCER_ENEMY_OUTLINE_COLOR,
    NECROMANCER_SCORE_MULTIPLIER,
    NECROMANCER_SUMMON_INTERVAL,
)


class NecromancerEnemy(Enemy):
    """Permanece en su punto de aparición mientras prepara invocaciones."""

    def __init__(
        self,
        word: str,
        start_position: tuple[float, float],
        target_position: tuple[float, float],
        speed: float = ENEMY_SPEED,
    ) -> None:
        super().__init__(word, start_position, target_position, speed)
        self.enemy_type = EnemyType.NECROMANCER
        self.score_multiplier = NECROMANCER_SCORE_MULTIPLIER
        self.label_color = NECROMANCER_ENEMY_COLOR
        self.summon_elapsed = 0.0
        self.summons_made = 0

    def update(self, delta_time: float) -> None:
        """Acumula tiempo para invocar sin alterar su posición."""

        self.summon_elapsed = min(
            NECROMANCER_SUMMON_INTERVAL,
            self.summon_elapsed + max(0.0, delta_time),
        )

    @property
    def ready_to_summon(self) -> bool:
        return self.summon_elapsed >= NECROMANCER_SUMMON_INTERVAL

    def mark_summoned(self) -> None:
        """Inicia la espera de la siguiente invocación."""

        self.summon_elapsed = 0.0
        self.summons_made += 1

    def draw(self, surface: pygame.Surface) -> None:
        """Muestra una figura de respaldo si faltan sus fotogramas."""

        center = (round(self.position.x), round(self.position.y))
        pygame.draw.circle(
            surface, NECROMANCER_ENEMY_OUTLINE_COLOR, center, self.radius + 4
        )
        pygame.draw.circle(surface, NECROMANCER_ENEMY_COLOR, center, self.radius)
        pygame.draw.circle(
            surface, NECROMANCER_ENEMY_CORE_COLOR, center, self.radius // 3
        )
