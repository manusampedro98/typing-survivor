"""Carga y anima la representación visual del jugador."""

from pathlib import Path

import pygame

from game.settings import (
    BACKGROUND_COLOR,
    PLAYER_COLOR,
    PLAYER_ATTACK_FPS,
    PLAYER_DAMAGE_FPS,
    PLAYER_DEATH_FPS,
    PLAYER_IDLE_FPS,
    PLAYER_OUTLINE_COLOR,
    PLAYER_POSITION,
    PLAYER_RADIUS,
    PLAYER_REVIVE_FPS,
    PLAYER_SPRITE_BOTTOM_Y,
    PLAYER_SPRITE_SIZE,
    PLAYER_TYPING_HOLD_DURATION,
)


DEFAULT_IDLE_DIRECTORY = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "images"
    / "player"
    / "idle"
)
DEFAULT_ATTACK_DIRECTORY = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "images"
    / "player"
    / "attack"
)
DEFAULT_DAMAGE_DIRECTORY = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "images"
    / "player"
    / "damage"
)
DEFAULT_DEATH_DIRECTORY = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "images"
    / "player"
    / "death"
)


class PlayerRenderer:
    """Gestiona las animaciones visuales del jugador."""

    def __init__(
        self,
        screen: pygame.Surface,
        body_font: pygame.font.Font,
    ) -> None:
        """Carga los recursos una vez y prepara el primer fotograma."""

        self.screen = screen
        self.body_font = body_font
        self.idle_frames = self._load_frames(
            DEFAULT_IDLE_DIRECTORY,
            "player_idle",
            frame_count=4,
        )
        self.attack_frames = self._load_frames(
            DEFAULT_ATTACK_DIRECTORY,
            "player_attack",
            frame_count=6,
        )
        self.damage_frames = self._load_frames(
            DEFAULT_DAMAGE_DIRECTORY,
            "player_damage",
            frame_count=3,
        )
        self.death_frames = self._load_frames(
            DEFAULT_DEATH_DIRECTORY,
            "player_death",
            frame_count=7,
        )
        self.revive_frames = list(reversed(self.death_frames))
        self.current_animation = "idle"
        self.current_frame_index = 0
        self.frame_elapsed_time = 0.0
        self.typing_time_remaining = 0.0
        self.death_finished = False

    def register_keystroke(self) -> None:
        """Mantiene activo el ciclo de tecleo tras una pulsación."""

        if (
            not self.attack_frames
            or self.current_animation in ("damage", "death", "revive")
        ):
            return

        # La primera letra inicia la secuencia; las siguientes prolongan el
        # ciclo sin reiniciarlo para conservar un movimiento fluido.
        if self.current_animation != "typing":
            self.current_animation = "typing"
            self.current_frame_index = 0
            self.frame_elapsed_time = 0.0

        self.typing_time_remaining = PLAYER_TYPING_HOLD_DURATION

    def play_damage(self) -> None:
        """Reproduce una reacción breve sin interrumpir la partida."""

        if not self.damage_frames or self.current_animation == "death":
            return

        self._start_animation("damage")

    def play_death(self) -> None:
        """Inicia la derrota y conserva visible su último fotograma."""

        self.death_finished = False

        if not self.death_frames:
            self.death_finished = True
            return

        self._start_animation("death")

    def play_revive(self) -> None:
        """Reconstruye al jugador reutilizando la muerte en orden inverso."""

        if not self.revive_frames:
            self.reset()
            return

        self._start_animation("revive")

    def reset(self) -> None:
        """Devuelve inmediatamente al jugador a su animación normal."""

        self.current_animation = "idle"
        self.current_frame_index = 0
        self.frame_elapsed_time = 0.0
        self.typing_time_remaining = 0.0
        self.death_finished = False

    def _start_animation(self, animation_name: str) -> None:
        """Reinicia una animación de una sola reproducción."""

        self.current_animation = animation_name
        self.current_frame_index = 0
        self.frame_elapsed_time = 0.0
        self.typing_time_remaining = 0.0

    def update(self, delta_time: float) -> None:
        """Avanza la animación con una velocidad independiente de los FPS."""

        if self.current_animation == "typing":
            self.typing_time_remaining = max(
                0.0,
                self.typing_time_remaining - delta_time,
            )

            if self.typing_time_remaining == 0.0:
                self.current_animation = "idle"
                self.current_frame_index = 0
                self.frame_elapsed_time = 0.0

        frames = self._get_current_frames()

        if len(frames) < 2:
            return

        animation_fps = self._get_animation_fps()
        frame_duration = 1.0 / animation_fps
        self.frame_elapsed_time += delta_time

        # El while conserva el ritmo si un fotograma tarda más de lo esperado.
        while self.frame_elapsed_time >= frame_duration:
            self.frame_elapsed_time -= frame_duration
            self.current_frame_index += 1

            if self.current_frame_index >= len(frames):
                if self.current_animation in ("idle", "typing"):
                    self.current_frame_index = 0
                elif self.current_animation == "death":
                    self.current_frame_index = len(frames) - 1
                    self.death_finished = True
                    self.frame_elapsed_time = 0.0
                    break
                else:
                    self.reset()
                    break

    def draw(self) -> None:
        """Dibuja el fotograma actual o una figura segura de respaldo."""

        frames = self._get_current_frames()

        if not frames:
            self._draw_fallback()
            return

        current_frame = frames[self.current_frame_index]
        current_frame = self._apply_animation_color(current_frame)
        shake_offset = self._get_shake_offset()
        frame_rect = current_frame.get_rect(
            midbottom=(
                round(PLAYER_POSITION[0]) + shake_offset[0],
                round(PLAYER_SPRITE_BOTTOM_Y) + shake_offset[1],
            )
        )
        self.screen.blit(current_frame, frame_rect)

    def _apply_animation_color(
        self,
        frame: pygame.Surface,
    ) -> pygame.Surface:
        """Añade color a daño, muerte y reaparición sin alterar los PNG."""

        if self.current_animation not in ("damage", "death", "revive"):
            return frame

        colored_frame = frame.copy()

        if self.current_animation == "damage":
            colored_frame.fill((85, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
        elif self.current_animation == "death":
            progress = self.current_frame_index / max(1, len(self.death_frames) - 1)
            shade = round(255 - 105 * progress)
            colored_frame.fill(
                (shade, shade, shade),
                special_flags=pygame.BLEND_RGB_MULT,
            )
        else:
            progress = self.current_frame_index / max(1, len(self.revive_frames) - 1)
            cyan_strength = round(90 * (1.0 - progress))
            colored_frame.fill(
                (0, cyan_strength, cyan_strength),
                special_flags=pygame.BLEND_RGB_ADD,
            )

        return colored_frame

    def _get_shake_offset(self) -> tuple[int, int]:
        """Desplaza brevemente el sprite para reforzar la recepción de daño."""

        if self.current_animation != "damage":
            return (0, 0)

        offsets = ((-5, 1), (6, -2), (-3, 0))
        return offsets[min(self.current_frame_index, len(offsets) - 1)]

    @staticmethod
    def _load_frames(
        directory: Path,
        file_prefix: str,
        frame_count: int,
    ) -> list[pygame.Surface]:
        """Carga una secuencia ordenada o la descarta si está incompleta."""

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
                frames.append(
                    pygame.transform.smoothscale(frame, PLAYER_SPRITE_SIZE)
                )
        except (pygame.error, OSError):
            return []

        return frames

    def _get_current_frames(self) -> list[pygame.Surface]:
        """Devuelve la secuencia correspondiente al estado visual actual."""

        if self.current_animation == "typing" and self.attack_frames:
            return self.attack_frames
        if self.current_animation == "damage" and self.damage_frames:
            return self.damage_frames
        if self.current_animation == "death" and self.death_frames:
            return self.death_frames
        if self.current_animation == "revive" and self.revive_frames:
            return self.revive_frames

        return self.idle_frames

    def _get_animation_fps(self) -> float:
        """Selecciona el ritmo apropiado para cada secuencia."""

        animation_speeds = {
            "typing": PLAYER_ATTACK_FPS,
            "damage": PLAYER_DAMAGE_FPS,
            "death": PLAYER_DEATH_FPS,
            "revive": PLAYER_REVIVE_FPS,
        }
        return animation_speeds.get(self.current_animation, PLAYER_IDLE_FPS)

    def _draw_fallback(self) -> None:
        """Conserva un jugador visible si los sprites no pueden cargarse."""

        player_center = (
            round(PLAYER_POSITION[0]),
            round(PLAYER_POSITION[1]),
        )
        pygame.draw.circle(
            self.screen,
            PLAYER_OUTLINE_COLOR,
            player_center,
            PLAYER_RADIUS + 5,
        )
        pygame.draw.circle(
            self.screen,
            PLAYER_COLOR,
            player_center,
            PLAYER_RADIUS,
        )

        player_label = self.body_font.render("P", True, BACKGROUND_COLOR)
        player_label_rect = player_label.get_rect(center=player_center)
        self.screen.blit(player_label, player_label_rect)
