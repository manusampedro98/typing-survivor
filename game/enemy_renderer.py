"""Carga y anima la representación visual de los enemigos."""

from dataclasses import dataclass
import math
from pathlib import Path

import pygame

from game.enemy import Enemy
from game.enemy_type import EnemyType
from game.settings import (
    ARMORED_ENEMY_DEATH_FPS,
    ARMORED_ENEMY_IDLE_FPS,
    ARMORED_ENEMY_SHIELD_BREAK_FPS,
    BOSS_VISIBLE_SIZE,
    BOSS_IDLE_FPS,
    BOSS_DAMAGE_FPS,
    BOSS_SUMMON_FPS,
    BOSS_DEATH_FPS,
    ENEMY_ARRIVAL_SIZE,
    FAST_ENEMY_DAMAGE_FPS,
    FAST_ENEMY_DEATH_FPS,
    FAST_ENEMY_FLIGHT_BOB_HEIGHT,
    FAST_ENEMY_FLIGHT_ROLL,
    FAST_ENEMY_FLIGHT_SPEED,
    FAST_ENEMY_IDLE_FPS,
    GOBLIN_ENEMY_DAMAGE_FPS,
    GOBLIN_ENEMY_DEATH_FPS,
    GOBLIN_ENEMY_IDLE_FPS,
    MIN_ENEMY_PERSPECTIVE_SCALE,
    NECROMANCER_ENEMY_DAMAGE_FPS,
    NECROMANCER_ENEMY_DEATH_FPS,
    NECROMANCER_ENEMY_IDLE_FPS,
    NECROMANCER_ENEMY_SUMMON_FPS,
    NECROMANCER_VISIBLE_SIZE,
    NORMAL_ENEMY_DAMAGE_FPS,
    NORMAL_ENEMY_DEATH_FPS,
    NORMAL_ENEMY_IDLE_FPS,
    SKELETON_ENEMY_DAMAGE_FPS,
    SKELETON_ENEMY_DEATH_FPS,
    SKELETON_ENEMY_IDLE_FPS,
)


ASSETS_ROOT = Path(__file__).resolve().parent.parent / "assets" / "images"
ENEMY_IDLE_SEQUENCES = {
    EnemyType.NORMAL: (
        ASSETS_ROOT / "enemies" / "normal" / "idle",
        "normal_enemy_idle",
        2,
    ),
    EnemyType.FAST: (
        ASSETS_ROOT / "enemies" / "fast" / "idle",
        "fast_enemy_idle",
        4,
    ),
    EnemyType.ARMORED: (
        ASSETS_ROOT / "enemies" / "armored" / "idle",
        "armored_enemy_idle",
        3,
    ),
    EnemyType.GOBLIN: (
        ASSETS_ROOT / "enemies" / "goblin" / "idle",
        "goblin_enemy_idle",
        4,
    ),
    EnemyType.NECROMANCER: (
        ASSETS_ROOT / "enemies" / "necromancer" / "idle",
        "necromancer_enemy_idle",
        4,
    ),
    EnemyType.SKELETON: (
        ASSETS_ROOT / "enemies" / "skeleton" / "idle",
        "skeleton_enemy_idle",
        4,
    ),
    EnemyType.BOSS: (
        ASSETS_ROOT / "enemies" / "boss" / "idle",
        "remains_golem_idle",
        4,
    ),
}
ENEMY_DAMAGE_SEQUENCES = {
    EnemyType.NORMAL: (
        ASSETS_ROOT / "enemies" / "normal" / "damage",
        "normal_enemy_damage",
        3,
    ),
    EnemyType.FAST: (
        ASSETS_ROOT / "enemies" / "fast" / "damage",
        "fast_enemy_damage",
        3,
    ),
    EnemyType.ARMORED: (
        ASSETS_ROOT / "enemies" / "armored" / "shield_break",
        "armored_enemy_shield_break",
        3,
    ),
    EnemyType.GOBLIN: (
        ASSETS_ROOT / "enemies" / "goblin" / "damage",
        "goblin_enemy_damage",
        3,
    ),
    EnemyType.NECROMANCER: (
        ASSETS_ROOT / "enemies" / "necromancer" / "damage",
        "necromancer_enemy_damage",
        3,
    ),
    EnemyType.SKELETON: (
        ASSETS_ROOT / "enemies" / "skeleton" / "damage",
        "skeleton_enemy_damage",
        2,
    ),
    EnemyType.BOSS: (
        ASSETS_ROOT / "enemies" / "boss" / "damage",
        "remains_golem_damage",
        3,
    ),
}
ENEMY_DEATH_SEQUENCES = {
    EnemyType.NORMAL: (
        ASSETS_ROOT / "enemies" / "normal" / "death",
        "normal_enemy_death",
        6,
    ),
    EnemyType.FAST: (
        ASSETS_ROOT / "enemies" / "fast" / "death",
        "fast_enemy_death",
        6,
    ),
    EnemyType.ARMORED: (
        ASSETS_ROOT / "enemies" / "armored" / "death",
        "armored_enemy_death",
        6,
    ),
    EnemyType.GOBLIN: (
        ASSETS_ROOT / "enemies" / "goblin" / "death",
        "goblin_enemy_death",
        6,
    ),
    EnemyType.NECROMANCER: (
        ASSETS_ROOT / "enemies" / "necromancer" / "death",
        "necromancer_enemy_death",
        6,
    ),
    EnemyType.SKELETON: (
        ASSETS_ROOT / "enemies" / "skeleton" / "death",
        "skeleton_enemy_death",
        6,
    ),
    EnemyType.BOSS: (
        ASSETS_ROOT / "enemies" / "boss" / "death",
        "remains_golem_death",
        6,
    ),
}
ENEMY_SUMMON_SEQUENCES = {
    EnemyType.NECROMANCER: (
        ASSETS_ROOT / "enemies" / "necromancer" / "summon",
        "necromancer_enemy_summon",
        6,
    ),
    EnemyType.BOSS: (
        ASSETS_ROOT / "enemies" / "boss" / "summon",
        "remains_golem_summon",
        6,
    ),
}
ENEMY_BROKEN_SEQUENCES = {
    EnemyType.ARMORED: (
        ASSETS_ROOT / "enemies" / "armored" / "broken_walk",
        "armored_enemy_broken_walk",
        3,
    ),
}
ENEMY_IDLE_FPS = {
    EnemyType.NORMAL: NORMAL_ENEMY_IDLE_FPS,
    EnemyType.FAST: FAST_ENEMY_IDLE_FPS,
    EnemyType.ARMORED: ARMORED_ENEMY_IDLE_FPS,
    EnemyType.GOBLIN: GOBLIN_ENEMY_IDLE_FPS,
    EnemyType.NECROMANCER: NECROMANCER_ENEMY_IDLE_FPS,
    EnemyType.SKELETON: SKELETON_ENEMY_IDLE_FPS,
    EnemyType.BOSS: BOSS_IDLE_FPS,
}
ENEMY_DAMAGE_FPS = {
    EnemyType.NORMAL: NORMAL_ENEMY_DAMAGE_FPS,
    EnemyType.FAST: FAST_ENEMY_DAMAGE_FPS,
    EnemyType.ARMORED: ARMORED_ENEMY_SHIELD_BREAK_FPS,
    EnemyType.GOBLIN: GOBLIN_ENEMY_DAMAGE_FPS,
    EnemyType.NECROMANCER: NECROMANCER_ENEMY_DAMAGE_FPS,
    EnemyType.SKELETON: SKELETON_ENEMY_DAMAGE_FPS,
    EnemyType.BOSS: BOSS_DAMAGE_FPS,
}
ENEMY_DEATH_FPS = {
    EnemyType.NORMAL: NORMAL_ENEMY_DEATH_FPS,
    EnemyType.FAST: FAST_ENEMY_DEATH_FPS,
    EnemyType.ARMORED: ARMORED_ENEMY_DEATH_FPS,
    EnemyType.GOBLIN: GOBLIN_ENEMY_DEATH_FPS,
    EnemyType.NECROMANCER: NECROMANCER_ENEMY_DEATH_FPS,
    EnemyType.SKELETON: SKELETON_ENEMY_DEATH_FPS,
    EnemyType.BOSS: BOSS_DEATH_FPS,
}


@dataclass
class TimedEnemyAnimation:
    """Controla una secuencia temporal asociada a un enemigo vivo."""

    name: str
    fps: float
    frame_index: int = 0
    elapsed_time: float = 0.0

    def update(self, delta_time: float, frame_count: int) -> bool:
        """Avanza la secuencia y devuelve True cuando ha terminado."""

        if frame_count == 0:
            return True

        frame_duration = 1.0 / self.fps
        self.elapsed_time += delta_time

        while self.elapsed_time >= frame_duration:
            self.elapsed_time -= frame_duration
            self.frame_index += 1

            if self.frame_index >= frame_count:
                return True

        return False


@dataclass
class EnemyDefeatAnimation:
    """Conserva una muerte visible después de retirar la entidad lógica."""

    enemy_type: EnemyType
    position: pygame.Vector2
    canvas_size: tuple[int, int]
    frame_references: list[tuple[str, int]]
    frame_durations: list[float]
    frame_index: int = 0
    elapsed_time: float = 0.0

    def update(self, delta_time: float) -> bool:
        """Avanza la reacción y devuelve True al consumir el último frame."""

        self.elapsed_time += delta_time

        while self.frame_index < len(self.frame_references):
            frame_duration = self.frame_durations[self.frame_index]
            if self.elapsed_time < frame_duration:
                break

            self.elapsed_time -= frame_duration
            self.frame_index += 1

        return self.frame_index >= len(self.frame_references)


class EnemyRenderer:
    """Reutiliza recursos y conserva alineadas todas las animaciones."""

    def __init__(self) -> None:
        """Carga las secuencias disponibles y prepara sus estados."""

        self.frames: dict[
            EnemyType,
            dict[str, list[pygame.Surface]],
        ] = {}

        for enemy_type, sequence in ENEMY_IDLE_SEQUENCES.items():
            self.frames[enemy_type] = {
                "idle": self._load_sequence(*sequence)
            }

        for enemy_type, sequence in ENEMY_DAMAGE_SEQUENCES.items():
            animation_name = (
                "shield_break"
                if enemy_type is EnemyType.ARMORED
                else "damage"
            )
            self.frames[enemy_type][animation_name] = self._load_sequence(
                *sequence
            )

        for enemy_type, sequence in ENEMY_SUMMON_SEQUENCES.items():
            self.frames[enemy_type]["summon"] = self._load_sequence(
                *sequence
            )

        for enemy_type, sequence in ENEMY_BROKEN_SEQUENCES.items():
            self.frames[enemy_type]["broken_walk"] = self._load_sequence(
                *sequence
            )

        for enemy_type, sequence in ENEMY_DEATH_SEQUENCES.items():
            self.frames[enemy_type]["death"] = self._load_sequence(
                *sequence
            )

        # Mantiene acceso directo al primer idle para tolerar recursos ausentes.
        self.images = {
            enemy_type: animations["idle"][0]
            if animations["idle"]
            else None
            for enemy_type, animations in self.frames.items()
        }
        self.reference_bounds = {
            enemy_type: self._get_visible_bounds(image)
            for enemy_type, image in self.images.items()
        }
        self.scaled_frames: dict[
            tuple[EnemyType, str, int, int, int], pygame.Surface
        ] = {}
        self.active_animations: dict[Enemy, TimedEnemyAnimation] = {}
        self.defeat_animations: list[EnemyDefeatAnimation] = []
        self.fast_enemy_shadows: dict[tuple[int, int], pygame.Surface] = {}
        self.animation_time = 0.0

    def update(self, delta_time: float) -> None:
        """Avanza idle, reacciones de daño, muertes y vuelo."""

        self.animation_time += delta_time

        for enemy, animation in list(self.active_animations.items()):
            frame_count = len(
                self.frames.get(enemy.enemy_type, {}).get(
                    animation.name,
                    [],
                )
            )
            if animation.update(delta_time, frame_count):
                self.active_animations.pop(enemy, None)

        active_defeats = []
        for animation in self.defeat_animations:
            if not animation.update(delta_time):
                active_defeats.append(animation)
        self.defeat_animations = active_defeats

    def play_damage(self, enemy: Enemy) -> None:
        """Reproduce la reacción disponible sin detener el movimiento."""

        animation_name = (
            "shield_break"
            if enemy.enemy_type is EnemyType.ARMORED
            else "damage"
        )
        frames = self.frames.get(enemy.enemy_type, {}).get(
            animation_name,
            [],
        )
        if not frames:
            return

        self.active_animations[enemy] = TimedEnemyAnimation(
            name=animation_name,
            fps=ENEMY_DAMAGE_FPS.get(
                enemy.enemy_type,
                NORMAL_ENEMY_DAMAGE_FPS,
            ),
        )

    def play_summon(self, enemy: Enemy) -> None:
        """Reproduce el conjuro al crear un esqueleto."""

        frames = self.frames.get(enemy.enemy_type, {}).get("summon", [])
        if frames:
            self.active_animations[enemy] = TimedEnemyAnimation(
                name="summon",
                fps=(
                    BOSS_SUMMON_FPS
                    if enemy.enemy_type is EnemyType.BOSS
                    else NECROMANCER_ENEMY_SUMMON_FPS
                ),
            )

    def play_death(self, enemy: Enemy) -> None:
        """Encadena daño y muerte en la posición del impacto final."""

        animations = self.frames.get(enemy.enemy_type, {})
        damage_frames = animations.get("damage", [])
        death_frames = animations.get("death", [])

        if not death_frames:
            return

        frame_references = [
            ("damage", index)
            for index in range(len(damage_frames))
        ] + [
            ("death", index)
            for index in range(len(death_frames))
        ]
        damage_fps = ENEMY_DAMAGE_FPS.get(
            enemy.enemy_type,
            NORMAL_ENEMY_DAMAGE_FPS,
        )
        death_fps = ENEMY_DEATH_FPS.get(
            enemy.enemy_type,
            NORMAL_ENEMY_DEATH_FPS,
        )
        frame_durations = [
            1.0 / damage_fps
        ] * len(damage_frames) + [
            1.0 / death_fps
        ] * len(death_frames)

        defeat_position = pygame.Vector2(enemy.position)
        if enemy.enemy_type is EnemyType.FAST:
            vertical_offset, _ = self._get_fast_enemy_motion(enemy)
            defeat_position.y += vertical_offset

        self.defeat_animations.append(
            EnemyDefeatAnimation(
                enemy_type=enemy.enemy_type,
                position=defeat_position,
                canvas_size=self._get_canvas_dimensions(enemy),
                frame_references=frame_references,
                frame_durations=frame_durations,
            )
        )
        self.active_animations.pop(enemy, None)

    def reset(self, preserve_boss_death: bool = False) -> None:
        """Elimina reacciones antiguas y conserva la muerte final si procede."""

        self.active_animations.clear()
        self.defeat_animations = (
            [
                animation for animation in self.defeat_animations
                if animation.enemy_type is EnemyType.BOSS
            ]
            if preserve_boss_death else []
        )
        self.animation_time = 0.0

    def draw(self, surface: pygame.Surface, enemy: Enemy) -> None:
        """Dibuja la animación activa o utiliza la figura de respaldo."""

        animation_name, frame_index = self._get_enemy_frame(enemy)
        frame = self._get_frame(
            enemy.enemy_type,
            animation_name,
            frame_index,
        )
        if frame is None:
            enemy.draw(surface)
            return

        canvas_size = self._get_canvas_dimensions(enemy)
        scaled_frame = self._get_scaled_frame(
            enemy.enemy_type,
            animation_name,
            frame_index,
            canvas_size,
        )
        center_x = round(enemy.position.x)
        center_y = round(enemy.position.y)

        if enemy.enemy_type is EnemyType.FAST:
            self._draw_fast_enemy(
                surface,
                enemy,
                scaled_frame,
                center_x,
                center_y,
            )
            return

        destination = scaled_frame.get_rect(center=(center_x, center_y))
        surface.blit(scaled_frame, destination)

    def draw_defeats(self, surface: pygame.Surface) -> None:
        """Dibuja las muertes aunque la entidad ya no acepte objetivos."""

        for animation in self.defeat_animations:
            animation_name, frame_index = animation.frame_references[
                animation.frame_index
            ]
            frame = self._get_scaled_frame(
                animation.enemy_type,
                animation_name,
                frame_index,
                animation.canvas_size,
            )
            if animation.enemy_type in (EnemyType.GOBLIN, EnemyType.SKELETON):
                # Todos sus fotogramas apoyan los pies en la misma línea.
                destination = frame.get_rect(
                    midbottom=(
                        round(animation.position.x),
                        round(animation.position.y)
                        + animation.canvas_size[1] // 2,
                    )
                )
            else:
                destination = frame.get_rect(
                    center=(
                        round(animation.position.x),
                        round(animation.position.y),
                    )
                )
            surface.blit(frame, destination)

    def get_draw_dimensions(self, enemy: Enemy) -> tuple[int, int]:
        """Calcula la silueta visible conservando la proporción original."""

        bounds = self.reference_bounds.get(enemy.enemy_type)
        if bounds is None or bounds.width == 0 or bounds.height == 0:
            fallback_size = enemy.radius * 2
            return (fallback_size, fallback_size)

        target_longest_side = (
            BOSS_VISIBLE_SIZE
            if enemy.enemy_type is EnemyType.BOSS
            else NECROMANCER_VISIBLE_SIZE
            if enemy.enemy_type is EnemyType.NECROMANCER
            else ENEMY_ARRIVAL_SIZE * self._get_perspective_scale(enemy)
        )
        image_scale = target_longest_side / max(bounds.size)
        return (
            max(1, round(bounds.width * image_scale)),
            max(1, round(bounds.height * image_scale)),
        )

    def get_draw_height(self, enemy: Enemy) -> int:
        """Devuelve la altura visible utilizada para colocar la palabra."""

        return self.get_draw_dimensions(enemy)[1]

    def _get_canvas_dimensions(self, enemy: Enemy) -> tuple[int, int]:
        """Devuelve el tamaño visible de referencia para todos los frames."""

        return self.get_draw_dimensions(enemy)

    def _get_enemy_frame(self, enemy: Enemy) -> tuple[str, int]:
        """Selecciona el frame de daño o el idle correspondiente."""

        active_animation = self.active_animations.get(enemy)
        if active_animation is not None:
            return (active_animation.name, active_animation.frame_index)

        if (
            enemy.enemy_type is EnemyType.ARMORED
            and enemy.health < enemy.max_health
        ):
            broken_frames = self.frames[enemy.enemy_type].get(
                "broken_walk",
                [],
            )
            if broken_frames:
                frame_index = int(
                    self.animation_time * ARMORED_ENEMY_IDLE_FPS
                ) % len(broken_frames)
                return ("broken_walk", frame_index)

        idle_frames = self.frames.get(enemy.enemy_type, {}).get("idle", [])
        if not idle_frames:
            return ("idle", 0)

        idle_fps = ENEMY_IDLE_FPS.get(
            enemy.enemy_type,
            NORMAL_ENEMY_IDLE_FPS,
        )
        frame_index = int(self.animation_time * idle_fps) % len(idle_frames)
        return ("idle", frame_index)

    def _get_scaled_frame(
        self,
        enemy_type: EnemyType,
        animation_name: str,
        frame_index: int,
        canvas_size: tuple[int, int],
    ) -> pygame.Surface:
        """Reutiliza cada combinación de frame y tamaño ya escalada."""

        cache_key = (
            enemy_type,
            animation_name,
            frame_index,
            canvas_size[0],
            canvas_size[1],
        )
        scaled_frame = self.scaled_frames.get(cache_key)

        if scaled_frame is None:
            frame = self.frames[enemy_type][animation_name][frame_index]
            visible_bounds = self._get_visible_bounds(frame)
            if enemy_type is EnemyType.BOSS:
                # El lienzo común conserva el tamaño del golem entre poses.
                reference = self.reference_bounds[EnemyType.BOSS]
                scale = max(canvas_size) / max(reference.size)
                scaled_frame = pygame.transform.smoothscale(
                    frame,
                    (
                        max(1, round(frame.get_width() * scale)),
                        max(1, round(frame.get_height() * scale)),
                    ),
                )
            elif visible_bounds is None or max(visible_bounds.size) == 0:
                scaled_frame = pygame.transform.smoothscale(
                    frame,
                    canvas_size,
                )
            else:
                # Cada pose conserva el mismo tamaño visible aunque el PNG
                # original deje márgenes transparentes diferentes.
                target_longest_side = max(canvas_size)
                scale = target_longest_side / max(visible_bounds.size)
                scaled_size = (
                    max(1, round(visible_bounds.width * scale)),
                    max(1, round(visible_bounds.height * scale)),
                )
                visible_frame = frame.subsurface(visible_bounds)
                scaled_frame = pygame.transform.smoothscale(
                    visible_frame,
                    scaled_size,
                )
            self.scaled_frames[cache_key] = scaled_frame

        return scaled_frame

    def _get_frame(
        self,
        enemy_type: EnemyType,
        animation_name: str,
        frame_index: int,
    ) -> pygame.Surface | None:
        """Obtiene un frame de forma segura cuando falta un recurso."""

        frames = self.frames.get(enemy_type, {}).get(animation_name, [])
        if not frames or frame_index >= len(frames):
            return None
        return frames[frame_index]

    @staticmethod
    def _get_perspective_scale(enemy: Enemy) -> float:
        """Interpola la escala según la distancia recorrida sin escalones."""

        total_distance = enemy.start_position.distance_to(
            enemy.target_position
        )
        if total_distance == 0:
            progress = 1.0
        else:
            remaining_distance = enemy.position.distance_to(
                enemy.target_position
            )
            progress = 1.0 - min(1.0, remaining_distance / total_distance)

        return MIN_ENEMY_PERSPECTIVE_SCALE + (
            (1.0 - MIN_ENEMY_PERSPECTIVE_SCALE) * progress
        )

    def _draw_fast_enemy(
        self,
        surface: pygame.Surface,
        enemy: Enemy,
        image: pygame.Surface,
        center_x: int,
        center_y: int,
    ) -> None:
        """Añade flotación, balanceo y sombra al murciélago."""

        vertical_offset, roll = self._get_fast_enemy_motion(enemy)

        self._draw_fast_enemy_shadow(
            surface,
            center_x,
            center_y,
            image.get_width(),
            image.get_height(),
        )

        flying_image = pygame.transform.rotozoom(image, roll, 1.0)
        destination = flying_image.get_rect(
            center=(center_x, round(center_y + vertical_offset))
        )
        surface.blit(flying_image, destination)

    def _get_fast_enemy_motion(
        self,
        enemy: Enemy,
    ) -> tuple[float, float]:
        """Calcula la altura y la inclinación actuales del vuelo."""

        phase = (
            self.animation_time * FAST_ENEMY_FLIGHT_SPEED
            + enemy.start_position.x * 0.012
        )
        return (
            math.sin(phase) * FAST_ENEMY_FLIGHT_BOB_HEIGHT,
            math.sin(phase * 0.75) * FAST_ENEMY_FLIGHT_ROLL,
        )

    def _draw_fast_enemy_shadow(
        self,
        surface: pygame.Surface,
        center_x: int,
        center_y: int,
        image_width: int,
        image_height: int,
    ) -> None:
        """Dibuja una sombra fija que separa al murciélago del suelo."""

        shadow_size = (
            max(8, round(image_width * 0.48)),
            max(4, round(image_height * 0.12)),
        )
        shadow = self.fast_enemy_shadows.get(shadow_size)

        if shadow is None:
            shadow = pygame.Surface(shadow_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 90), shadow.get_rect())
            self.fast_enemy_shadows[shadow_size] = shadow

        shadow_rect = shadow.get_rect(
            center=(center_x, center_y + image_height // 2 + 10)
        )
        surface.blit(shadow, shadow_rect)

    @staticmethod
    def _get_visible_bounds(
        image: pygame.Surface | None,
    ) -> pygame.Rect | None:
        """Mide la silueta ignorando restos casi transparentes."""

        if image is None:
            return None
        return image.get_bounding_rect(min_alpha=8)

    @staticmethod
    def _load_sequence(
        directory: Path,
        prefix: str,
        frame_count: int,
    ) -> list[pygame.Surface]:
        """Carga una secuencia completa o la descarta si falta un frame."""

        frame_paths = [
            directory / f"{prefix}_{index:02}.png"
            for index in range(1, frame_count + 1)
        ]
        if not all(frame_path.is_file() for frame_path in frame_paths):
            return []

        try:
            return [
                pygame.image.load(str(frame_path)).convert_alpha()
                for frame_path in frame_paths
            ]
        except (pygame.error, OSError):
            return []
