"""Efectos visuales breves para reforzar las acciones del jugador."""

from dataclasses import dataclass
from math import tau
from random import uniform

import pygame

from game.power_up_assets import load_power_up_icon
from game.power_up_type import PowerUpType
from game.settings import (
    ACCENT_COLOR, BOSS_WAVE_INTERVAL, INCORRECT_COLOR,
    WINDOW_HEIGHT, WINDOW_WIDTH,
)


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

        title = (
            f"JEFE · OLEADA {self.wave_number}"
            if self.wave_number % BOSS_WAVE_INTERVAL == 0
            else f"OLEADA {self.wave_number}"
        )
        text_surface = font.render(
            title,
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


@dataclass
class ExpandingPulse:
    """Onda que nace en el jugador y se desvanece al cruzar la arena."""

    position: pygame.Vector2
    color: tuple[int, int, int]
    delay: float = 0.0
    lifetime: float = 1.05
    max_radius: int = 930
    age: float = 0.0

    @property
    def is_alive(self) -> bool:
        return self.age < self.delay + self.lifetime

    def update(self, delta_time: float) -> None:
        self.age += delta_time

    def draw(self, canvas: pygame.Surface) -> None:
        if self.age < self.delay:
            return
        progress = min(1.0, (self.age - self.delay) / self.lifetime)
        radius = round(32 + (self.max_radius - 32) * progress)
        alpha = round(190 * (1.0 - progress) ** 1.3)
        center = (round(self.position.x), round(self.position.y))
        pygame.draw.circle(
            canvas, (*self.color, max(0, alpha // 4)), center, radius, width=15
        )
        pygame.draw.circle(
            canvas, (*self.color, alpha), center, radius, width=4
        )


@dataclass
class OneUpHeart:
    """Corazón verde con flecha ascendente al ganar una vida."""

    position: pygame.Vector2
    color: tuple[int, int, int]
    lifetime: float = 1.55
    age: float = 0.0

    @property
    def is_alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, delta_time: float) -> None:
        self.age += delta_time

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        progress = min(1.0, self.age / self.lifetime)
        alpha = round(255 * min(1.0, (1.0 - progress) / 0.28))
        canvas = pygame.Surface((190, 96), pygame.SRCALPHA)
        outline = (24, 72, 48, alpha)
        fill = (*self.color, alpha)
        highlight = (205, 255, 216, alpha)

        pygame.draw.line(canvas, outline, (35, 75), (35, 38), width=9)
        pygame.draw.line(canvas, fill, (35, 74), (35, 38), width=5)
        pygame.draw.polygon(canvas, outline, ((19, 43), (35, 17), (51, 43)))
        pygame.draw.polygon(canvas, fill, ((24, 40), (35, 21), (46, 40)))
        pygame.draw.circle(canvas, outline, (85, 38), 15)
        pygame.draw.circle(canvas, outline, (109, 38), 15)
        pygame.draw.polygon(canvas, outline, ((70, 42), (124, 42), (97, 76)))
        pygame.draw.circle(canvas, fill, (85, 38), 12)
        pygame.draw.circle(canvas, fill, (109, 38), 12)
        pygame.draw.polygon(canvas, fill, ((73, 42), (121, 42), (97, 71)))
        pygame.draw.circle(canvas, highlight, (83, 34), 4)

        label = font.render("+1UP", True, self.color)
        label.set_alpha(alpha)
        canvas.blit(label, label.get_rect(center=(151, 48)))
        draw_position = (
            round(self.position.x - canvas.get_width() / 2),
            round(self.position.y - 48 - 78 * progress),
        )
        surface.blit(canvas, draw_position)


@dataclass
class ShieldImpact:
    """Hace aparecer el emblema al absorber un golpe."""

    position: pygame.Vector2
    image: pygame.Surface
    lifetime: float = 0.55
    age: float = 0.0

    @property
    def is_alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, delta_time: float) -> None:
        self.age += delta_time

    def draw(self, surface: pygame.Surface) -> None:
        progress = min(1.0, self.age / self.lifetime)
        scale = 0.75 + progress * 0.8
        size = (
            max(1, round(self.image.get_width() * scale)),
            max(1, round(self.image.get_height() * scale)),
        )
        emblem = pygame.transform.smoothscale(self.image, size)
        emblem.set_alpha(round(245 * (1.0 - progress) ** 1.5))
        surface.blit(
            emblem,
            emblem.get_rect(center=(round(self.position.x), round(self.position.y))),
        )


@dataclass
class PowerUpDrop:
    """Icono de recompensa que asciende desde el enemigo derrotado."""

    position: pygame.Vector2
    image: pygame.Surface
    color: tuple[int, int, int]
    lifetime: float = 1.15
    age: float = 0.0

    @property
    def is_alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, delta_time: float) -> None:
        self.age += delta_time

    def draw(self, surface: pygame.Surface) -> None:
        progress = min(1.0, self.age / self.lifetime)
        fade = min(1.0, (1.0 - progress) / 0.3)
        size = round(44 + 7 * min(1.0, progress / 0.2))
        scale = size / max(self.image.get_size())
        image = pygame.transform.smoothscale(
            self.image,
            (
                max(1, round(self.image.get_width() * scale)),
                max(1, round(self.image.get_height() * scale)),
            ),
        )
        image.set_alpha(round(255 * fade))
        center = (
            max(36, min(WINDOW_WIDTH - 36, round(self.position.x + 32))),
            max(42, round(self.position.y - 28 - 54 * progress)),
        )
        halo = pygame.Surface((68, 68), pygame.SRCALPHA)
        pygame.draw.circle(halo, (*self.color, round(42 * fade)), (34, 34), 30)
        pygame.draw.circle(halo, (*self.color, round(145 * fade)),
                           (34, 34), 28, width=2)
        surface.blit(halo, halo.get_rect(center=center))
        surface.blit(image, image.get_rect(center=center))


class EffectManager:
    """Crea, actualiza y dibuja todos los efectos temporales."""

    def __init__(self) -> None:
        """Prepara colecciones vacías de partículas y textos."""

        self.particles: list[Particle] = []
        self.floating_texts: list[FloatingText] = []
        self.wave_announcement: WaveAnnouncement | None = None
        self.expanding_pulses: list[ExpandingPulse] = []
        self.one_up_hearts: list[OneUpHeart] = []
        self.shield_impacts: list[ShieldImpact] = []
        self.power_up_drops: list[PowerUpDrop] = []
        self._shield_icon = load_power_up_icon(PowerUpType.SHIELD, 108)
        self._drop_icons = {
            power_up: icon
            for power_up in PowerUpType
            if (icon := load_power_up_icon(power_up, 48)) is not None
        }
        self._pulse_canvas: pygame.Surface | None = None

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

        if awarded_points == 0:
            # El rebote mantiene partículas e impacto sin texto sobre la arena.
            if defeated:
                return
            feedback_text = "ESCUDO -1"
        elif defeated:
            feedback_text = f"+{awarded_points}"
        else:
            feedback_text = f"ESCUDO -1  +{awarded_points}"
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

    def create_power_up_drop(
        self,
        position: pygame.Vector2 | tuple[float, float],
        power_up: PowerUpType,
    ) -> None:
        """Muestra el icono de la recompensa en el punto de la baja."""

        origin = pygame.Vector2(position)
        icon = self._drop_icons.get(power_up)
        if icon is not None:
            self.power_up_drops.append(PowerUpDrop(origin, icon, power_up.color))
        self._create_burst(origin, power_up.color, 12, 150)

    def create_power_up_burst(
        self,
        position: pygame.Vector2 | tuple[float, float],
        color: tuple[int, int, int],
    ) -> None:
        """Confirma una activación sin mostrar texto flotante."""

        self._create_burst(pygame.Vector2(position), color, 14, 160)

    def create_emp_pulse(
        self,
        position: tuple[float, float],
        color: tuple[int, int, int],
    ) -> None:
        """Emite tres ondas escalonadas desde el jugador."""

        origin = pygame.Vector2(position)
        self.expanding_pulses.extend(
            ExpandingPulse(pygame.Vector2(origin), color, delay=index * 0.16)
            for index in range(3)
        )

    def create_shield_block(
        self,
        position: tuple[float, float],
        color: tuple[int, int, int],
    ) -> None:
        """Hace estallar la barrera en chispas y dos ondas cercanas."""

        origin = pygame.Vector2(position)
        self._create_burst(
            origin, color, particle_count=28, maximum_speed=230
        )
        self.expanding_pulses.extend((
            ExpandingPulse(
                pygame.Vector2(origin), color,
                lifetime=0.48, max_radius=190,
            ),
            ExpandingPulse(
                pygame.Vector2(origin), (40, 215, 255), delay=0.09,
                lifetime=0.5, max_radius=220,
            ),
        ))
        if self._shield_icon is not None:
            self.shield_impacts.append(
                ShieldImpact(
                    pygame.Vector2(origin.x, origin.y - 45), self._shield_icon
                )
            )

    def create_one_up_heart(
        self,
        position: tuple[float, float],
        color: tuple[int, int, int],
    ) -> None:
        """Muestra una vida ganada con un corazón y una flecha."""

        self._create_burst(
            pygame.Vector2(position), color, particle_count=18,
            maximum_speed=150,
        )
        self.one_up_hearts.append(OneUpHeart(pygame.Vector2(position), color))

    def update(self, delta_time: float) -> None:
        """Actualiza los efectos y descarta los que han terminado."""

        for particle in self.particles:
            particle.update(delta_time)
        for pulse in self.expanding_pulses:
            pulse.update(delta_time)
        for heart in self.one_up_hearts:
            heart.update(delta_time)
        for impact in self.shield_impacts:
            impact.update(delta_time)
        for drop in self.power_up_drops:
            drop.update(delta_time)
        for floating_text in self.floating_texts:
            floating_text.update(delta_time)
        if self.wave_announcement is not None:
            self.wave_announcement.update(delta_time)

        self.particles = [
            particle
            for particle in self.particles
            if particle.is_alive
        ]
        self.expanding_pulses = [pulse for pulse in self.expanding_pulses if pulse.is_alive]
        self.one_up_hearts = [
            heart for heart in self.one_up_hearts if heart.is_alive
        ]
        self.shield_impacts = [
            impact for impact in self.shield_impacts if impact.is_alive
        ]
        self.power_up_drops = [
            drop for drop in self.power_up_drops if drop.is_alive
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

        if self.expanding_pulses:
            if self._pulse_canvas is None:
                self._pulse_canvas = pygame.Surface(
                    (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
                )
            self._pulse_canvas.fill((0, 0, 0, 0))
            for pulse in self.expanding_pulses:
                pulse.draw(self._pulse_canvas)
            surface.blit(self._pulse_canvas, (0, 0))
        for particle in self.particles:
            particle.draw(surface)
        for impact in self.shield_impacts:
            impact.draw(surface)
        for drop in self.power_up_drops:
            drop.draw(surface)
        for floating_text in self.floating_texts:
            floating_text.draw(surface, font)
        for heart in self.one_up_hearts:
            heart.draw(surface, font)

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
        self.expanding_pulses.clear()
        self.one_up_hearts.clear()
        self.shield_impacts.clear()
        self.power_up_drops.clear()
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
