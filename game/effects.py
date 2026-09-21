"""Efectos visuales breves para reforzar las acciones del jugador."""

from dataclasses import dataclass
from math import tau
from random import uniform

import pygame

from game.settings import ACCENT_COLOR, INCORRECT_COLOR, POWER_UP_COLOR


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


@dataclass
class WaveAnnouncement:
    """Texto animado que comunica el comienzo de una nueva oleada."""

    wave_number: int
    lifetime: float = 2.2
    age: float = 0.0

    @property
    def is_alive(self) -> bool:
        """Indica si la animación debe continuar visible."""

        return self.age < self.lifetime

    def update(self, delta_time: float) -> None:
        """Avanza el tiempo de la animación sin detener la partida."""

        self.age += delta_time

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
    ) -> None:
        """Aplica escala, desplazamiento y transparencia al texto."""

        progress = min(1.0, self.age / self.lifetime)
        scale = 1.0
        vertical_offset = 0

        if progress < 0.18:
            # La entrada asciende mientras aumenta desde el 75 % de su tamaño.
            entrance_progress = progress / 0.18
            alpha = round(255 * entrance_progress)
            scale = 0.75 + 0.25 * entrance_progress
            vertical_offset = round(30 * (1.0 - entrance_progress))
        elif progress > 0.72:
            # La salida invierte el recorrido y baja mientras se desvanece.
            exit_progress = (progress - 0.72) / 0.28
            alpha = round(255 * (1.0 - exit_progress))
            vertical_offset = round(30 * exit_progress)
        else:
            alpha = 255

        text_surface = font.render(
            f"OLEADA {self.wave_number}",
            True,
            ACCENT_COLOR,
        )
        scaled_size = (
            max(1, round(text_surface.get_width() * scale)),
            max(1, round(text_surface.get_height() * scale)),
        )
        text_surface = pygame.transform.smoothscale(
            text_surface,
            scaled_size,
        )
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(
            center=(
                surface.get_width() // 2,
                round(surface.get_height() * 0.42) + vertical_offset,
            )
        )
        surface.blit(text_surface, text_rect)


class EffectManager:
    """Crea, actualiza y dibuja todos los efectos temporales."""

    def __init__(self) -> None:
        """Prepara colecciones vacías de partículas y textos."""

        self.particles: list[Particle] = []
        self.floating_texts: list[FloatingText] = []
        self.wave_announcement: WaveAnnouncement | None = None

    def create_wave_announcement(self, wave_number: int) -> None:
        """Inicia el aviso de la nueva oleada."""

        self.wave_announcement = WaveAnnouncement(wave_number)

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

    def create_player_death(
        self,
        position: tuple[float, float],
    ) -> None:
        """Refuerza la derrota con una explosión roja más intensa."""

        self._create_burst(
            pygame.Vector2(position),
            INCORRECT_COLOR,
            particle_count=34,
            maximum_speed=270,
        )

    def create_player_revive(
        self,
        position: tuple[float, float],
    ) -> None:
        """Acompaña el reinicio con energía cian y un mensaje breve."""

        revive_position = pygame.Vector2(position)
        self._create_burst(
            revive_position,
            ACCENT_COLOR,
            particle_count=26,
            maximum_speed=190,
        )
        self.floating_texts.append(
            FloatingText(
                text="REINICIANDO",
                position=revive_position,
                color=ACCENT_COLOR,
                lifetime=1.1,
            )
        )

    def create_power_up_feedback(
        self,
        position: pygame.Vector2 | tuple[float, float],
        text: str,
    ) -> None:
        """Destaca la obtención o activación de una ralentización."""

        effect_position = pygame.Vector2(position)
        self._create_burst(
            effect_position,
            POWER_UP_COLOR,
            particle_count=14,
            maximum_speed=160,
        )
        self.floating_texts.append(
            FloatingText(
                text=text,
                position=effect_position,
                color=POWER_UP_COLOR,
                lifetime=1.2,
            )
        )

    def update(self, delta_time: float) -> None:
        """Actualiza los efectos y descarta los que han terminado."""

        for particle in self.particles:
            particle.update(delta_time)
        for floating_text in self.floating_texts:
            floating_text.update(delta_time)
        if self.wave_announcement is not None:
            self.wave_announcement.update(delta_time)

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

        if (
            self.wave_announcement is not None
            and not self.wave_announcement.is_alive
        ):
            self.wave_announcement = None

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

    def draw_wave_announcement(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
    ) -> None:
        """Dibuja el aviso por encima de la interfaz cuando está activo."""

        if self.wave_announcement is not None:
            self.wave_announcement.draw(surface, font)

    def reset(self) -> None:
        """Elimina todos los efectos de la partida anterior."""

        self.particles.clear()
        self.floating_texts.clear()
        self.wave_announcement = None

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
