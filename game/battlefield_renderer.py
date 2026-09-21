"""Representación visual del campo de batalla."""

from pathlib import Path

import pygame

from game.effects import EffectManager
from game.enemy import Enemy
from game.enemy_manager import EnemyManager
from game.enemy_renderer import EnemyRenderer
from game.player_renderer import PlayerRenderer
from game.projectile_manager import ProjectileManager
from game.settings import (
    ARENA_BACKGROUND_DARKEN_ALPHA,
    BACKGROUND_COLOR,
    CORRECT_COLOR,
    ENEMY_LANE_START_POSITIONS,
    INCORRECT_COLOR,
    LANE_COLOR,
    LANE_HIGHLIGHT_COLOR,
    LANE_SHADOW_COLOR,
    PLAYER_POSITION,
    POINTS_PER_CHARACTER,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


DEFAULT_BACKGROUND_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "images"
    / "backgrounds"
    / "arena_background.png"
)


class BattlefieldRenderer:
    """Dibuja elementos de combate sin modificar su estado."""

    def __init__(
        self,
        screen: pygame.Surface,
        target_font: pygame.font.Font,
        body_font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        """Recibe la superficie y las fuentes creadas por el juego."""

        self.screen = screen
        self.target_font = target_font
        self.body_font = body_font
        self.small_font = small_font

        # El jugador mantiene su propia carga de sprites y reloj de animación.
        self.player_renderer = PlayerRenderer(screen, body_font)
        self.enemy_renderer = EnemyRenderer()

        # El fondo se carga y escala una sola vez, no en cada fotograma.
        self.background = self._load_background(DEFAULT_BACKGROUND_PATH)
        self.background_tint = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA,
        )
        self.background_tint.fill(
            (0, 0, 0, ARENA_BACKGROUND_DARKEN_ALPHA)
        )

    def update(self, delta_time: float) -> None:
        """Actualiza las animaciones visuales del campo de batalla."""

        self.player_renderer.update(delta_time)
        self.enemy_renderer.update(delta_time)

    def register_player_keystroke(self) -> None:
        """Mantiene al jugador tecleando mientras recibe caracteres."""

        self.player_renderer.register_keystroke()

    def play_player_damage(self) -> None:
        """Activa la reacción visual a la pérdida de una vida."""

        self.player_renderer.play_damage()

    def play_enemy_damage(self, enemy: Enemy) -> None:
        """Activa la reacción visual del enemigo que conserva vida."""

        self.enemy_renderer.play_damage(enemy)

    def play_enemy_death(self, enemy: Enemy) -> None:
        """Conserva visible la derrota después de retirar el objetivo."""

        self.enemy_renderer.play_death(enemy)

    def reset_enemy_animations(self) -> None:
        """Descarta reacciones pertenecientes a la partida anterior."""

        self.enemy_renderer.reset()

    def play_player_death(self) -> None:
        """Activa la animación final del jugador."""

        self.player_renderer.play_death()

    def play_player_revive(self) -> None:
        """Reproduce la secuencia inversa al comenzar de nuevo."""

        self.player_renderer.play_revive()

    def reset_player_animation(self) -> None:
        """Devuelve el jugador al idle al iniciar una partida normal."""

        self.player_renderer.reset()

    @property
    def is_player_death_finished(self) -> bool:
        """Indica cuándo puede mostrarse la pantalla de resultado."""

        return self.player_renderer.death_finished

    def draw(
        self,
        enemy_manager: EnemyManager,
        active_enemy: Enemy | None,
        typed_text: str,
        effect_manager: EffectManager,
        projectile_manager: ProjectileManager,
    ) -> None:
        """Dibuja carriles, entidades, palabras y efectos temporales."""

        self._draw_background()
        self._draw_lanes()

        for enemy in enemy_manager.enemies:
            self.enemy_renderer.draw(self.screen, enemy)

        self.enemy_renderer.draw_defeats(self.screen)

        self.player_renderer.draw()
        projectile_manager.draw(self.screen)

        # Los efectos quedan sobre las figuras y bajo las palabras legibles.
        effect_manager.draw(self.screen, self.small_font)
        self._draw_enemy_words(
            enemy_manager.enemies,
            active_enemy,
            typed_text,
        )

    def draw_menu_background(self) -> None:
        """Dibuja únicamente el fondo limpio para las pantallas del menú."""

        self._draw_background()

    @staticmethod
    def _load_background(
        background_path: Path,
    ) -> pygame.Surface | None:
        """Carga el fondo optimizado y tolera recursos ausentes o dañados."""

        try:
            background = pygame.image.load(str(background_path)).convert()
        except (pygame.error, OSError):
            return None

        if background.get_size() != (WINDOW_WIDTH, WINDOW_HEIGHT):
            background = pygame.transform.smoothscale(
                background,
                (WINDOW_WIDTH, WINDOW_HEIGHT),
            )

        return background

    def _draw_background(self) -> None:
        """Dibuja la arena ilustrada o utiliza el color plano de respaldo."""

        if self.background is None:
            self.screen.fill(BACKGROUND_COLOR)
            return

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.background_tint, (0, 0))

    def _draw_lanes(self) -> None:
        """Dibuja los carriles que convergen en el jugador."""

        lane_end = (
            round(PLAYER_POSITION[0]),
            round(PLAYER_POSITION[1]),
        )

        for lane_start in ENEMY_LANE_START_POSITIONS:
            start_position = (
                round(lane_start[0]),
                round(lane_start[1]),
            )
            pygame.draw.line(
                self.screen,
                LANE_SHADOW_COLOR,
                start_position,
                lane_end,
                width=7,
            )
            pygame.draw.line(
                self.screen,
                LANE_COLOR,
                start_position,
                lane_end,
                width=3,
            )
            pygame.draw.line(
                self.screen,
                LANE_HIGHLIGHT_COLOR,
                start_position,
                lane_end,
                width=1,
            )

    def _draw_enemy_words(
        self,
        enemies: list[Enemy],
        active_enemy: Enemy | None,
        typed_text: str,
    ) -> None:
        """Dibuja la palabra y el estado de cada enemigo visible."""

        for enemy in enemies:
            self._draw_enemy_word(enemy, active_enemy, typed_text)

    def _draw_enemy_word(
        self,
        enemy: Enemy,
        active_enemy: Enemy | None,
        typed_text: str,
    ) -> None:
        """Dibuja una palabra y resalta el progreso del objetivo activo."""

        # La palabra completada desaparece mientras el proyectil viaja; el
        # enemigo sigue visible para recibir el impacto en pantalla.
        if enemy.is_pending_hit:
            return

        enemy_half_height = self.enemy_renderer.get_draw_height(enemy) // 2
        word_center_y = max(
            105,
            round(enemy.position.y) - enemy_half_height - 12,
        )
        type_center_y = max(75, word_center_y - 30)

        # La recompensa base explica la diferencia entre palabras cortas y largas.
        base_points = (
            len(enemy.word)
            * POINTS_PER_CHARACTER
            * enemy.score_multiplier
        )
        enemy_details = (
            f"{enemy.enemy_type.display_name}"
            f"  ·  {base_points} pts base"
        )

        if enemy.max_health > 1:
            shield_status = (
                f"Escudo {enemy.health}/{enemy.max_health}"
                if enemy.health == enemy.max_health
                else "Armadura rota"
            )
            enemy_details += f"  ·  {shield_status}"

        if enemy is active_enemy:
            enemy_details = f">  {enemy_details}"

        type_surface = self.small_font.render(
            enemy_details,
            True,
            enemy.label_color,
        )
        type_half_width = type_surface.get_width() // 2
        type_center_x = max(
            type_half_width + 20,
            min(
                round(enemy.position.x),
                WINDOW_WIDTH - type_half_width - 20,
            ),
        )
        type_rect = type_surface.get_rect(
            center=(
                type_center_x,
                type_center_y,
            )
        )
        self.screen.blit(type_surface, type_rect)

        character_surfaces = []

        # Solo el objetivo activo compara el texto introducido.
        for index, character in enumerate(enemy.word):
            if enemy is active_enemy and index < len(typed_text):
                character_color = (
                    CORRECT_COLOR
                    if typed_text[index] == character
                    else INCORRECT_COLOR
                )
            else:
                character_color = TEXT_COLOR

            character_surfaces.append(
                self.target_font.render(
                    character,
                    True,
                    character_color,
                )
            )

        total_width = sum(
            surface.get_width()
            for surface in character_surfaces
        )
        half_word_width = total_width // 2
        word_center_x = max(
            half_word_width + 20,
            min(
                round(enemy.position.x),
                WINDOW_WIDTH - half_word_width - 20,
            ),
        )
        character_x = word_center_x - half_word_width
        for character_surface in character_surfaces:
            character_rect = character_surface.get_rect(
                midleft=(character_x, word_center_y)
            )
            self.screen.blit(character_surface, character_rect)
            character_x += character_surface.get_width()
