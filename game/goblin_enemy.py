"""Goblin errático que cambia cinco veces de rumbo al acercarse."""

from random import uniform

import pygame

from game.enemy import Enemy
from game.enemy_type import EnemyType
from game.settings import (
    ENEMY_REACH_DISTANCE,
    ENEMY_SPEED,
    GOBLIN_ENEMY_COLOR,
    GOBLIN_ENEMY_CORE_COLOR,
    GOBLIN_ENEMY_OUTLINE_COLOR,
    GOBLIN_MAX_TURN_ANGLE,
    GOBLIN_RANDOM_MOVES,
    GOBLIN_WANDER_ANGLE,
    GOBLIN_WAYPOINT_ATTEMPTS,
    PLAYER_POSITION,
    WINDOW_WIDTH,
)


class GoblinEnemy(Enemy):
    """Avanza mediante cinco destinos aleatorios de distancia decreciente."""

    def __init__(
        self,
        word: str,
        start_position: tuple[float, float],
        target_position: tuple[float, float],
        speed: float = ENEMY_SPEED,
    ) -> None:
        super().__init__(word, start_position, target_position, speed)
        self.enemy_type = EnemyType.GOBLIN
        self.label_color = GOBLIN_ENEMY_COLOR
        self.random_moves_completed = 0
        self.last_angle = 0.0
        self.next_position = self._choose_waypoint()

    def update(self, delta_time: float) -> None:
        """Consume el tiempo del fotograma sin saltar ni atravesar destinos."""

        if delta_time <= 0.0 or self.speed <= 0.0:
            return

        remaining_time = delta_time
        while remaining_time > 0.0 and not self.has_reached_target():
            offset = self.next_position - self.position
            distance = offset.length()

            if distance <= ENEMY_REACH_DISTANCE:
                self.position.update(self.next_position)
                self._advance_waypoint()
                continue

            travel = self.speed * remaining_time
            if travel < distance:
                self.position += offset * (travel / distance)
                break

            self.position.update(self.next_position)
            remaining_time -= distance / self.speed
            self._advance_waypoint()

    def reset_to_start(self) -> None:
        """El EMP reinicia también el recorrido errático del goblin."""

        super().reset_to_start()
        self.random_moves_completed = 0
        self.last_angle = 0.0
        self.next_position = self._choose_waypoint()

    def _advance_waypoint(self) -> None:
        if self.random_moves_completed < GOBLIN_RANDOM_MOVES:
            self.random_moves_completed += 1
        self.next_position = self._choose_waypoint()

    def _choose_waypoint(self) -> pygame.Vector2:
        if self.random_moves_completed >= GOBLIN_RANDOM_MOVES:
            return pygame.Vector2(self.target_position)

        step = self.random_moves_completed + 1
        spawn_offset = self.start_position - self.target_position
        remaining_radius = spawn_offset.length() * (
            1.0 - step / (GOBLIN_RANDOM_MOVES + 1)
        )
        direction = spawn_offset.normalize()

        for _ in range(GOBLIN_WAYPOINT_ATTEMPTS):
            # El giro limitado mantiene decreciente la distancia al jugador.
            angle = uniform(
                max(-GOBLIN_WANDER_ANGLE, self.last_angle - GOBLIN_MAX_TURN_ANGLE),
                min(GOBLIN_WANDER_ANGLE, self.last_angle + GOBLIN_MAX_TURN_ANGLE),
            )
            candidate = self.target_position + direction.rotate(angle) * remaining_radius
            if (
                70.0 <= candidate.x <= WINDOW_WIDTH - 70.0
                and 165.0 <= candidate.y <= PLAYER_POSITION[1] - 15.0
            ):
                self.last_angle = angle
                return candidate

        self.last_angle = 0.0
        return self.target_position + direction * remaining_radius

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja una silueta de respaldo si falta algún sprite."""

        center = (round(self.position.x), round(self.position.y))
        pygame.draw.circle(
            surface,
            GOBLIN_ENEMY_OUTLINE_COLOR,
            center,
            self.radius + 4,
        )
        pygame.draw.circle(
            surface,
            GOBLIN_ENEMY_COLOR,
            center,
            self.radius,
        )
        pygame.draw.circle(
            surface,
            GOBLIN_ENEMY_CORE_COLOR,
            center,
            self.radius // 3,
        )
