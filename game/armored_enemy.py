"""Variante blindada de la entidad enemiga."""

import pygame

from game.enemy import Enemy
from game.enemy_type import EnemyType
from game.settings import (
    ARMORED_ENEMY_COLOR,
    ARMORED_ENEMY_CORE_COLOR,
    ARMORED_ENEMY_HEALTH,
    ARMORED_ENEMY_OUTLINE_COLOR,
    ARMORED_ENEMY_SCORE_MULTIPLIER,
    ARMORED_ENEMY_SPEED_MULTIPLIER,
    ENEMY_SPEED,
)


class ArmoredEnemy(Enemy):
    """Enemigo lento que requiere completar varias palabras."""

    def __init__(
        self,
        word: str,
        start_position: tuple[float, float],
        target_position: tuple[float, float],
        speed: float = ENEMY_SPEED,
    ) -> None:
        """Crea la variante con velocidad reducida y resistencia adicional."""

        super().__init__(
            word=word,
            start_position=start_position,
            target_position=target_position,
            speed=speed * ARMORED_ENEMY_SPEED_MULTIPLIER,
        )

        self.enemy_type = EnemyType.ARMORED
        self.score_multiplier = ARMORED_ENEMY_SCORE_MULTIPLIER
        self.label_color = ARMORED_ENEMY_COLOR
        self.max_health = ARMORED_ENEMY_HEALTH
        self.health = self.max_health
        self.second_word: str | None = None
        self.second_word_exposed = False

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja un hexágono que representa la armadura del enemigo."""

        center_x = round(self.position.x)
        center_y = round(self.position.y)

        outline_points = self._build_hexagon_points(
            center_x,
            center_y,
            self.radius + 5,
        )
        body_points = self._build_hexagon_points(
            center_x,
            center_y,
            self.radius,
        )

        pygame.draw.polygon(
            surface,
            ARMORED_ENEMY_OUTLINE_COLOR,
            outline_points,
        )
        pygame.draw.polygon(surface, ARMORED_ENEMY_COLOR, body_points)
        pygame.draw.circle(
            surface,
            ARMORED_ENEMY_CORE_COLOR,
            (center_x, center_y),
            self.radius // 3,
        )

    @staticmethod
    def _build_hexagon_points(
        center_x: int,
        center_y: int,
        radius: int,
    ) -> list[tuple[int, int]]:
        """Calcula los seis vértices de la silueta blindada."""

        half_radius = radius // 2
        return [
            (center_x - radius, center_y),
            (center_x - half_radius, center_y - radius),
            (center_x + half_radius, center_y - radius),
            (center_x + radius, center_y),
            (center_x + half_radius, center_y + radius),
            (center_x - half_radius, center_y + radius),
        ]
