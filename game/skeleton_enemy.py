"""Esqueleto invocado que avanza con una palabra breve."""

import pygame

from game.enemy import Enemy
from game.enemy_type import EnemyType
from game.settings import (
    ENEMY_SPEED,
    SKELETON_ENEMY_COLOR,
    SKELETON_ENEMY_CORE_COLOR,
    SKELETON_ENEMY_OUTLINE_COLOR,
    SKELETON_SPEED_MULTIPLIER,
    SKELETON_SCORE_MULTIPLIER,
)


class SkeletonEnemy(Enemy):
    """Avanza desde el nigromante y acepta palabras de tres letras."""

    def __init__(
        self,
        word: str,
        start_position: tuple[float, float],
        target_position: tuple[float, float],
        speed: float = ENEMY_SPEED,
        summoner: Enemy | None = None,
    ) -> None:
        if len(word) > 3:
            raise ValueError("La palabra de un esqueleto no puede superar tres letras.")
        super().__init__(
            word, start_position, target_position,
            speed * SKELETON_SPEED_MULTIPLIER,
        )
        self.enemy_type = EnemyType.SKELETON
        self.score_multiplier = SKELETON_SCORE_MULTIPLIER
        self.label_color = SKELETON_ENEMY_COLOR
        self.summoner = summoner

    def draw(self, surface: pygame.Surface) -> None:
        """Muestra una figura de respaldo si faltan sus fotogramas."""

        center = (round(self.position.x), round(self.position.y))
        pygame.draw.circle(
            surface, SKELETON_ENEMY_OUTLINE_COLOR, center, self.radius + 4
        )
        pygame.draw.circle(surface, SKELETON_ENEMY_COLOR, center, self.radius)
        pygame.draw.circle(
            surface, SKELETON_ENEMY_CORE_COLOR, center, self.radius // 3
        )
