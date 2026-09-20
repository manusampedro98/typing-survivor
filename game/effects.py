"""Efectos visuales breves para reforzar las acciones del jugador."""

from dataclasses import dataclass
from math import tau
from random import uniform

import pygame

from game.settings import INCORRECT_COLOR


@dataclass
class Particle:
    """Partícula que se desplaza y reduce su tamaño hasta desaparecer."""

    position: pygame.Vector2
    velocity: pygame.Vector2
    color: tuple[int, int, int]
    lifetime: float
    initial_radius: float
    age: float = 0.0

    @property
    def is_alive(self) -> bool:
        """Indica si la partícula todavía debe actualizarse y dibujarse."""

        return self.age < self.lifetime

    def update(self, delta_time: float) -> None:
        """Actualiza posición, velocidad y tiempo de vida."""

        self.age += delta_time
        self.position += self.velocity * delta_time

        # La resistencia suaviza el movimiento al final de la animación.
        self.velocity *= 0.96 ** (delta_time * 60)

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja la partícula reduciéndola según su tiempo restante."""

        remaining_ratio = max(0.0, 1.0 - self.age / self.lifetime)
        radius = max(1, round(self.initial_radius * remaining_ratio))
        pygame.draw.circle(
            surface,
            self.color,
            (round(self.position.x), round(self.position.y)),
            radius,
        )


@dataclass
class FloatingText:
    """Texto que asciende y se desvanece después de una acción."""

    text: str
    position: pygame.Vector2
    color: tuple[int, int, int]
    lifetime: float = 0.9
    age: float = 0.0

    @property
    def is_alive(self) -> bool:
        """Indica si el texto todavía debe mostrarse."""

        return self.age < self.lifetime

    def update(self, delta_time: float) -> None:
        """Desplaza el texto hacia arriba durante su vida útil."""

        self.age += delta_time
        self.position.y -= 35 * delta_time

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
    ) -> None:
        """Dibuja el texto aplicando una transparencia progresiva."""

        remaining_ratio = max(0.0, 1.0 - self.age / self.lifetime)
        text_surface = font.render(self.text, True, self.color)
        text_surface.set_alpha(round(255 * remaining_ratio))
        text_rect = text_surface.get_rect(center=self.position)
        surface.blit(text_surface, text_rect)


class EffectManager:
    """Crea, actualiza y dibuja todos los efectos temporales."""

    def __init__(self) -> None:
        """Prepara colecciones vacías de partículas y textos."""

        self.particles: list[Particle] = []
        self.floating_texts: list[FloatingText] = []

    def create_enemy_feedback(
        self,
        position: pygame.Vector2,
        color: tuple[int, int, int],
        awarded_points: int,
        defeated: bool,
    ) -> None:
        """Genera una explosión y muestra la recompensa conseguida."""

        particle_count = 16 if defeated else 8
        maximum_speed = 180 if defeated else 110

        self._create_burst(
            position,
            color,
            particle_count,
            maximum_speed,
        )

        feedback_text = (
            f"+{awarded_points}"
            if defeated
            else f"ESCUDO -1  +{awarded_points}"
        )
        self.floating_texts.append(
            FloatingText(
                text=feedback_text,
                position=pygame.Vector2(position),
                color=color,
            )
        )

    def create_player_damage(
        self,
        position: tuple[float, float],
    ) -> None:
        """Genera una señal visual cuando el jugador pierde una vida."""

        self._create_burst(
            pygame.Vector2(position),
            INCORRECT_COLOR,
            particle_count=18,
            maximum_speed=210,
        )
        self.floating_texts.append(
            FloatingText(
                text="-1 VIDA",
                position=pygame.Vector2(position),
                color=INCORRECT_COLOR,
            )
        )

    def update(self, delta_time: float) -> None:
        """Actualiza los efectos y descarta los que han terminado."""

        for particle in self.particles:
            particle.update(delta_time)
        for floating_text in self.floating_texts:
            floating_text.update(delta_time)

        self.particles = [
            particle
            for particle in self.particles
            if particle.is_alive
        ]
        self.floating_texts = [
            floating_text
            for floating_text in self.floating_texts
            if floating_text.is_alive
        ]

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
    ) -> None:
        """Dibuja partículas y textos sobre el campo de batalla."""

        for particle in self.particles:
            particle.draw(surface)
        for floating_text in self.floating_texts:
            floating_text.draw(surface, font)

    def reset(self) -> None:
        """Elimina todos los efectos de la partida anterior."""

        self.particles.clear()
        self.floating_texts.clear()

    def _create_burst(
        self,
        position: pygame.Vector2,
        color: tuple[int, int, int],
        particle_count: int,
        maximum_speed: float,
    ) -> None:
        """Crea partículas que se expanden en direcciones aleatorias."""

        for _ in range(particle_count):
            direction = pygame.Vector2(1, 0).rotate_rad(uniform(0, tau))
            speed = uniform(maximum_speed * 0.45, maximum_speed)

            self.particles.append(
                Particle(
                    position=pygame.Vector2(position),
                    velocity=direction * speed,
                    color=color,
                    lifetime=uniform(0.35, 0.6),
                    initial_radius=uniform(3.0, 6.0),
                )
            )
