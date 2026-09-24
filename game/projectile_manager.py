"""Proyectiles dirigidos y animaciones de impacto del jugador."""

from dataclasses import dataclass, field
from pathlib import Path

import pygame

from game.enemy import Enemy
from game.settings import (
    ACCENT_COLOR,
    ENERGY_BALL_FPS,
    ENERGY_BALL_SIZE,
    ENERGY_IMPACT_FPS,
    ENERGY_IMPACT_SIZE,
    ENERGY_PROJECTILE_SPEED,
    PLAYER_PROJECTILE_ORIGIN,
)


EFFECTS_DIRECTORY = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "images"
    / "effects"
)


@dataclass
class EnergyHit:
    """Comunica a la partida qué enemigo debe recibir el impacto."""

    enemy: Enemy
    awarded_points: int
    position: pygame.Vector2


@dataclass
class EnergyProjectile:
    """Bola de energía que persigue la posición actual de un enemigo."""

    enemy: Enemy
    awarded_points: int
    position: pygame.Vector2
    remaining_targets: list[Enemy] = field(default_factory=list)
    frame_index: int = 0
    frame_elapsed_time: float = 0.0

    def update(self, delta_time: float, frame_count: int) -> bool:
        """Mueve y anima el proyectil; devuelve True al alcanzar el objetivo."""

        self._update_animation(delta_time, frame_count)
        offset = self.enemy.position - self.position
        remaining_distance = offset.length()
        movement_distance = ENERGY_PROJECTILE_SPEED * delta_time

        if remaining_distance <= movement_distance:
            self.position.update(self.enemy.position)
            return True

        if remaining_distance > 0.0:
            self.position += offset.normalize() * movement_distance

        return False

    def _update_animation(self, delta_time: float, frame_count: int) -> None:
        """Repite los fotogramas durante todo el recorrido."""

        if frame_count < 2:
            return

        frame_duration = 1.0 / ENERGY_BALL_FPS
        self.frame_elapsed_time += delta_time

        while self.frame_elapsed_time >= frame_duration:
            self.frame_elapsed_time -= frame_duration
            self.frame_index = (self.frame_index + 1) % frame_count


@dataclass
class EnergyImpact:
    """Animación de una sola reproducción situada sobre el punto de golpe."""

    position: pygame.Vector2
    frame_index: int = 0
    frame_elapsed_time: float = 0.0

    def update(self, delta_time: float, frame_count: int) -> None:
        """Avanza la explosión hasta superar su último fotograma."""

        if frame_count == 0:
            self.frame_elapsed_time += delta_time
            return

        frame_duration = 1.0 / ENERGY_IMPACT_FPS
        self.frame_elapsed_time += delta_time

        while self.frame_elapsed_time >= frame_duration:
            self.frame_elapsed_time -= frame_duration
            self.frame_index += 1

    def is_finished(self, frame_count: int) -> bool:
        """Indica si la explosión ya no necesita dibujarse."""

        if frame_count == 0:
            return self.frame_elapsed_time >= 0.4

        return self.frame_index >= frame_count


class ProjectileManager:
    """Carga recursos y coordina proyectiles e impactos simultáneos."""

    def __init__(self) -> None:
        """Carga todas las imágenes una sola vez."""

        self.ball_frames = self._load_frames(
            EFFECTS_DIRECTORY / "energy_ball",
            "energy_ball",
            frame_count=4,
            size=ENERGY_BALL_SIZE,
        )
        self.impact_frames = self._load_frames(
            EFFECTS_DIRECTORY / "energy_impact",
            "energy_impact",
            frame_count=6,
            size=ENERGY_IMPACT_SIZE,
        )
        self.projectiles: list[EnergyProjectile] = []
        self.impacts: list[EnergyImpact] = []

    def launch(self, enemy: Enemy, awarded_points: int) -> None:
        """Crea un proyectil asociado al enemigo que recibirá el daño."""

        self.projectiles.append(
            EnergyProjectile(
                enemy=enemy,
                awarded_points=awarded_points,
                position=pygame.Vector2(PLAYER_PROJECTILE_ORIGIN),
            )
        )

    def launch_chain(
        self,
        enemy: Enemy,
        chain_targets: list[Enemy],
        awarded_points: int,
    ) -> None:
        """Lanza una bola que rebota por los objetivos indicados."""

        self.projectiles.append(
            EnergyProjectile(
                enemy=enemy,
                awarded_points=awarded_points,
                position=pygame.Vector2(PLAYER_PROJECTILE_ORIGIN),
                remaining_targets=list(chain_targets),
            )
        )

    def update(self, delta_time: float) -> list[EnergyHit]:
        """Actualiza los efectos y devuelve los impactos de este fotograma."""

        energy_hits: list[EnergyHit] = []
        active_projectiles: list[EnergyProjectile] = []

        for projectile in self.projectiles:
            reached_target = projectile.update(
                delta_time,
                len(self.ball_frames),
            )

            if reached_target:
                impact_position = pygame.Vector2(projectile.enemy.position)
                self.impacts.append(EnergyImpact(impact_position))
                energy_hits.append(
                    EnergyHit(
                        enemy=projectile.enemy,
                        awarded_points=projectile.awarded_points,
                        position=impact_position,
                    )
                )

                if projectile.remaining_targets:
                    projectile.enemy = projectile.remaining_targets.pop(0)
                    projectile.awarded_points = 0
                    active_projectiles.append(projectile)
            else:
                active_projectiles.append(projectile)

        self.projectiles = active_projectiles

        for impact in self.impacts:
            impact.update(delta_time, len(self.impact_frames))

        self.impacts = [
            impact
            for impact in self.impacts
            if not impact.is_finished(len(self.impact_frames))
        ]
        return energy_hits

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja bolas e impactos, con formas de respaldo si falta el arte."""

        for projectile in self.projectiles:
            center = (
                round(projectile.position.x),
                round(projectile.position.y),
            )

            if self.ball_frames:
                frame = self.ball_frames[projectile.frame_index]
                surface.blit(frame, frame.get_rect(center=center))
            else:
                pygame.draw.circle(surface, ACCENT_COLOR, center, 12)

        for impact in self.impacts:
            center = (
                round(impact.position.x),
                round(impact.position.y),
            )

            if self.impact_frames:
                frame = self.impact_frames[impact.frame_index]
                surface.blit(frame, frame.get_rect(center=center))
            else:
                progress = min(1.0, impact.frame_elapsed_time / 0.4)
                radius = round(12 + 34 * progress)
                pygame.draw.circle(
                    surface,
                    ACCENT_COLOR,
                    center,
                    radius,
                    width=5,
                )

    def reset(self) -> None:
        """Descarta los efectos que pertenecían a la partida anterior."""

        self.projectiles.clear()
        self.impacts.clear()

    def cancel_target(self, enemy: Enemy) -> None:
        """Retira disparos cuyo objetivo ya ha alcanzado al jugador."""

        active_projectiles: list[EnergyProjectile] = []
        for projectile in self.projectiles:
            projectile.remaining_targets = [
                target
                for target in projectile.remaining_targets
                if target is not enemy
            ]
            if projectile.enemy is enemy:
                if not projectile.remaining_targets:
                    continue
                projectile.enemy = projectile.remaining_targets.pop(0)
                projectile.awarded_points = 0
            active_projectiles.append(projectile)
        self.projectiles = active_projectiles

    @staticmethod
    def _load_frames(
        directory: Path,
        file_prefix: str,
        frame_count: int,
        size: tuple[int, int],
    ) -> list[pygame.Surface]:
        """Carga una secuencia completa o activa el dibujo de respaldo."""

        frame_paths = [
            directory / f"{file_prefix}_{index:02}.png"
            for index in range(1, frame_count + 1)
        ]

        if not all(frame_path.is_file() for frame_path in frame_paths):
            return []

        frames: list[pygame.Surface] = []

        try:
            for frame_path in frame_paths:
                frame = pygame.image.load(str(frame_path)).convert_alpha()
                frames.append(pygame.transform.smoothscale(frame, size))
        except (pygame.error, OSError):
            return []

        return frames
