"""Representación visual del campo de batalla."""

import pygame

from game.effects import EffectManager
from game.enemy import Enemy
from game.enemy_manager import EnemyManager
from game.settings import (
    BACKGROUND_COLOR,
    CORRECT_COLOR,
    ENEMY_LANE_START_POSITIONS,
    INCORRECT_COLOR,
    LANE_COLOR,
    PLAYER_COLOR,
    PLAYER_OUTLINE_COLOR,
    PLAYER_POSITION,
    PLAYER_RADIUS,
    POINTS_PER_CHARACTER,
    TEXT_COLOR,
    WINDOW_WIDTH,
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

    def draw(
        self,
        enemy_manager: EnemyManager,
        active_enemy: Enemy | None,
        typed_text: str,
        effect_manager: EffectManager,
    ) -> None:
        """Dibuja carriles, entidades, palabras y efectos temporales."""

        self._draw_lanes()

        for enemy in enemy_manager.enemies:
            enemy.draw(self.screen)

        self._draw_player()

        # Los efectos quedan sobre las figuras y bajo las palabras legibles.
        effect_manager.draw(self.screen, self.small_font)
        self._draw_enemy_words(
            enemy_manager.enemies,
            active_enemy,
            typed_text,
        )

    def _draw_lanes(self) -> None:
        """Dibuja los carriles que convergen en el jugador."""

        lane_end = (
            round(PLAYER_POSITION[0]),
            round(PLAYER_POSITION[1]),
        )

        for lane_start in ENEMY_LANE_START_POSITIONS:
            pygame.draw.line(
                self.screen,
                LANE_COLOR,
                (round(lane_start[0]), round(lane_start[1])),
                lane_end,
                width=3,
            )

    def _draw_player(self) -> None:
        """Dibuja la representación provisional del jugador."""

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

        # La letra identifica temporalmente al jugador hasta añadir su sprite.
        player_label = self.body_font.render("P", True, BACKGROUND_COLOR)
        player_label_rect = player_label.get_rect(center=player_center)
        self.screen.blit(player_label, player_label_rect)

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
            enemy_details += (
                f"  ·  Escudo {enemy.health}/{enemy.max_health}"
            )

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
                max(75, round(enemy.position.y) - 82),
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
        word_center_y = max(105, round(enemy.position.y) - 47)

        for character_surface in character_surfaces:
            character_rect = character_surface.get_rect(
                midleft=(character_x, word_center_y)
            )
            self.screen.blit(character_surface, character_rect)
            character_x += character_surface.get_width()
