"""Entidad enemiga que avanza hacia un objetivo."""

import pygame

from game.enemy_type import EnemyType
from game.settings import (
    ENEMY_COLOR,
    ENEMY_CORE_COLOR,
    ENEMY_OUTLINE_COLOR,
    ENEMY_RADIUS,
    ENEMY_REACH_DISTANCE,
    ENEMY_SPEED,
)


class Enemy:
    """Representa un enemigo móvil asociado a una palabra."""

    def __init__(
        self,
        word: str,
        start_position: tuple[float, float],
        target_position: tuple[float, float],
        speed: float = ENEMY_SPEED,
    ) -> None:
        """Crea un enemigo y almacena los datos necesarios para moverlo."""

        self.word = word
        self.position = pygame.Vector2(start_position)
        self.start_position = pygame.Vector2(start_position)
        self.target_position = pygame.Vector2(target_position)
        self.speed = speed
        self.radius = ENEMY_RADIUS

        # Estos datos permiten mostrar y premiar distintos tipos de enemigo.
        self.enemy_type = EnemyType.NORMAL
        self.score_multiplier = 1
        self.label_color = ENEMY_COLOR
        self.max_health = 1
        self.health = self.max_health

        # El blindado puede mostrar su segunda palabra mientras el primer
        # disparo sigue en vuelo; el contador conserva ambos impactos.
        self.pending_hits = 0
        self.is_pending_hit = False

    def take_hit(self) -> bool:
        """Resta resistencia y devuelve si el enemigo ha sido eliminado."""

        self.health -= 1
        return self.health <= 0

    def update(self, delta_time: float) -> None:
        """Avanza hacia el objetivo de forma independiente de los FPS."""

        offset = self.target_position - self.position
        remaining_distance = offset.length()

        # Evita normalizar un vector de longitud cero al alcanzar el destino.
        if remaining_distance <= ENEMY_REACH_DISTANCE:
            self.position.update(self.target_position)
            return

        movement_distance = self.speed * delta_time

        # Impide que un fotograma lento haga que el enemigo sobrepase el objetivo.
        if movement_distance >= remaining_distance:
            self.position.update(self.target_position)
            return

        self.position += offset.normalize() * movement_distance

    def reset_to_start(self) -> None:
        """Devuelve al enemigo a su posición original tras el pulso EMP."""

        self.position.update(self.start_position)

    def has_reached_target(self) -> bool:
        """Indica si el enemigo ocupa exactamente la posición del jugador."""

        return self.position == self.target_position

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja una representación provisional del enemigo."""

        center = (round(self.position.x), round(self.position.y))

        # El contorno mejora la lectura de la silueta sobre fondos oscuros.
        pygame.draw.circle(
            surface,
            ENEMY_OUTLINE_COLOR,
            center,
            self.radius + 4,
        )
        pygame.draw.circle(
            surface,
            ENEMY_COLOR,
            center,
            self.radius,
        )

        # El núcleo aporta contraste mientras todavía no utilizamos sprites.
        pygame.draw.circle(
            surface,
            ENEMY_CORE_COLOR,
            center,
            self.radius // 3,
        )
