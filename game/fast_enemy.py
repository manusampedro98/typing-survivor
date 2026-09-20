"""Variante rápida de la entidad enemiga."""

import pygame

from game.enemy import Enemy
from game.enemy_type import EnemyType
from game.settings import (
    ENEMY_SPEED,
    FAST_ENEMY_COLOR,
    FAST_ENEMY_CORE_COLOR,
    FAST_ENEMY_OUTLINE_COLOR,
    FAST_ENEMY_SCORE_MULTIPLIER,
    FAST_ENEMY_SPEED_MULTIPLIER,
)


class FastEnemy(Enemy):
    """Enemigo más veloz que concede una recompensa adicional."""

    def __init__(
        self,
        word: str,
        start_position: tuple[float, float],
        target_position: tuple[float, float],
        speed: float = ENEMY_SPEED,
    ) -> None:
        """Crea la variante aplicando su multiplicador de velocidad."""

        super().__init__(
            word=word,
            start_position=start_position,
            target_position=target_position,
            speed=speed * FAST_ENEMY_SPEED_MULTIPLIER,
        )

        self.enemy_type = EnemyType.FAST
        self.score_multiplier = FAST_ENEMY_SCORE_MULTIPLIER
        self.label_color = FAST_ENEMY_COLOR

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja una silueta puntiaguda diferenciada del enemigo normal."""

        center_x = round(self.position.x)
        center_y = round(self.position.y)

        # La punta señala la dirección de avance hacia la base del jugador.
        outline_points = [
            (center_x + self.radius + 5, center_y),
            (center_x - self.radius - 4, center_y - self.radius - 4),
            (center_x - self.radius - 4, center_y + self.radius + 4),
        ]
        body_points = [
            (center_x + self.radius, center_y),
            (center_x - self.radius, center_y - self.radius),
            (center_x - self.radius, center_y + self.radius),
        ]

        pygame.draw.polygon(
            surface,
            FAST_ENEMY_OUTLINE_COLOR,
            outline_points,
        )
        pygame.draw.polygon(surface, FAST_ENEMY_COLOR, body_points)
        pygame.draw.circle(
            surface,
            FAST_ENEMY_CORE_COLOR,
            (center_x - self.radius // 4, center_y),
            self.radius // 4,
        )
