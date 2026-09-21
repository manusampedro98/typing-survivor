"""Representación visual de la interfaz y las pantallas del juego."""

from collections import Counter
import math

import pygame

from game.difficulty import Difficulty
from game.enemy_type import EnemyType
from game.game_state import GameState
from game.save_manager import HighScore
from game.settings import (
    ACCENT_COLOR,
    ARMORED_ENEMY_COLOR,
    ARMORED_ENEMY_CORE_COLOR,
    ARMORED_ENEMY_HEALTH,
    ARMORED_ENEMY_OUTLINE_COLOR,
    BACKGROUND_COLOR,
    BOTTOM_HUD_HEIGHT,
    BOTTOM_HUD_TOP,
    BORDER_COLOR,
    CARET_HEIGHT,
    CARET_WIDTH,
    COMBO_BAR_HEIGHT,
    COMBO_BAR_WIDTH,
    ENEMY_COLOR,
    ENEMY_CORE_COLOR,
    ENEMY_OUTLINE_COLOR,
    FAST_ENEMY_COLOR,
    FAST_ENEMY_CORE_COLOR,
    FAST_ENEMY_OUTLINE_COLOR,
    GAME_OVER_OVERLAY_COLOR,
    INCORRECT_COLOR,
    INPUT_BOX_CENTER_X,
    INPUT_BOX_CENTER_Y,
    INPUT_BOX_HEIGHT,
    INPUT_BOX_WIDTH,
    INPUT_HORIZONTAL_PADDING,
    HUD_PANEL_MARGIN,
    MAX_COMBO_MULTIPLIER,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
    POWER_UP_COLOR,
    POWER_UP_SLOT_GAP,
    POWER_UP_SLOT_SIZE,
    RESTART_OVERLAY_ALPHA,
    SLOW_POWER_UP_DURATION,
    STARTING_LIVES,
    TEXT_COLOR,
    TOP_HUD_HEIGHT,
    TOP_HUD_TOP,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    WORDS_PER_WAVE,
)
from game.typing_stats import TypingStats
from game.wave_manager import WaveManager


MAIN_MENU_ACTIONS = (
    "JUGAR",
    "OPCIONES",
    "AYUDA",
    "SALIR",
    "CRÉDITOS",
    "CONTACTO",
)
MAIN_MENU_BUTTONS = tuple(
    pygame.Rect(WINDOW_WIDTH // 2 - 175, 218 + index * 66, 350, 52)
    for index in range(4)
)
MENU_CREDITS_BUTTON = pygame.Rect(30, WINDOW_HEIGHT - 55, 112, 32)
MENU_CONTACT_BUTTON = pygame.Rect(152, WINDOW_HEIGHT - 55, 112, 32)
DIFFICULTY_CARDS = tuple(
    pygame.Rect(125 + index * 350, 235, 300, 250)
    for index in range(3)
)
OPTIONS_PANEL = pygame.Rect(WINDOW_WIDTH // 2 - 330, 120, 660, 465)
OPTIONS_CLOSE_BUTTON = pygame.Rect(OPTIONS_PANEL.right - 48, 136, 32, 32)
OPTIONS_SLIDER = pygame.Rect(WINDOW_WIDTH // 2 - 210, 305, 420, 18)
OPTIONS_MUTE_BUTTON = pygame.Rect(410, 365, 220, 52)
OPTIONS_FULLSCREEN_BUTTON = pygame.Rect(650, 365, 220, 52)
HELP_CLOSE_BUTTON = pygame.Rect(1170, 50, 32, 32)
INFO_CLOSE_BUTTON = pygame.Rect(972, 160, 32, 32)
LINKEDIN_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 - 245, 425, 220, 52)
GITHUB_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 + 25, 425, 220, 52)


class UIRenderer:
    """Dibuja el HUD, el campo de escritura y las capas de estado."""

    main_menu_actions = MAIN_MENU_ACTIONS

    def __init__(
        self,
        screen: pygame.Surface,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        """Recibe la superficie y reutiliza las fuentes del juego."""

        self.screen = screen
        self.title_font = title_font
        self.body_font = body_font
        self.small_font = small_font

    def draw_interface(
        self,
        typed_text: str,
        caret_visible: bool,
        score: int,
        combo: int,
        combo_multiplier: int,
        combo_progress: float,
        lives: int,
        typing_stats: TypingStats,
        wave_manager: WaveManager,
        slow_charge_available: bool,
        slow_time_remaining: float,
    ) -> None:
        """Dibuja la información de la partida y el campo de escritura."""

        self._draw_top_hud(
            score=score,
            lives=lives,
            wave_manager=wave_manager,
        )
        self._draw_bottom_hud(
            typed_text=typed_text,
            caret_visible=caret_visible,
            combo=combo,
            combo_multiplier=combo_multiplier,
            combo_progress=combo_progress,
            typing_stats=typing_stats,
            slow_charge_available=slow_charge_available,
            slow_time_remaining=slow_time_remaining,
        )

    def draw_state_overlay(
        self,
        state: GameState,
        countdown_remaining: float,
        high_score: HighScore,
        is_new_high_score: bool,
        score: int,
        completed_words: int,
        wave_manager: WaveManager,
        defeated_enemies: Counter[EnemyType],
        typing_stats: TypingStats,
        audio_volume: float,
        audio_muted: bool,
        is_fullscreen: bool,
        menu_selection: int,
        difficulty_selection: int,
        restarting: bool,
    ) -> None:
        """Dibuja la pantalla superpuesta que corresponde al estado actual."""

        if state is GameState.MENU:
            self._draw_menu(high_score, menu_selection)
        elif state is GameState.DIFFICULTY:
            self._draw_difficulty(difficulty_selection)
        elif state is GameState.OPTIONS:
            self._draw_options(
                audio_volume,
                audio_muted,
                is_fullscreen,
            )
        elif state is GameState.CREDITS:
            self._draw_information_screen(
                "CRÉDITOS",
                (
                    "Typing Survivor",
                    "Diseño, programación y dirección: Manu",
                    "Proyecto personal desarrollado con Python y Pygame.",
                ),
            )
        elif state is GameState.CONTACT:
            self._draw_information_screen(
                "CONTACTO",
                (
                    "Para propuestas y consultas, utiliza los canales",
                    "indicados en el perfil del proyecto.",
                ),
            )
        elif state is GameState.COUNTDOWN:
            self._draw_countdown(countdown_remaining, restarting)
        elif state is GameState.PAUSED:
            self._draw_pause(audio_volume, audio_muted)
        elif state is GameState.HELP:
            self._draw_help(is_fullscreen)
        elif state is GameState.GAME_OVER:
            self._draw_game_over(
                high_score=high_score,
                is_new_high_score=is_new_high_score,
                score=score,
                completed_words=completed_words,
                wave_manager=wave_manager,
                defeated_enemies=defeated_enemies,
                typing_stats=typing_stats,
            )

    @staticmethod
    def get_menu_action_at(position: tuple[int, int]) -> str | None:
        """Devuelve la acción del botón principal situado bajo el puntero."""

        for action, button_rect in zip(
            MAIN_MENU_ACTIONS[:4],
            MAIN_MENU_BUTTONS,
        ):
            if button_rect.collidepoint(position):
                return action

        if MENU_CREDITS_BUTTON.collidepoint(position):
            return "CRÉDITOS"
        if MENU_CONTACT_BUTTON.collidepoint(position):
            return "CONTACTO"
        return None

    @staticmethod
    def get_options_control_at(position: tuple[int, int]) -> str | None:
        """Identifica el control de opciones situado bajo el puntero."""

        controls = (
            ("CERRAR", OPTIONS_CLOSE_BUTTON),
            ("VOLUMEN", OPTIONS_SLIDER.inflate(0, 24)),
            ("MUTE", OPTIONS_MUTE_BUTTON),
            ("PANTALLA_COMPLETA", OPTIONS_FULLSCREEN_BUTTON),
        )
        for action, control_rect in controls:
            if control_rect.collidepoint(position):
                return action
        return None

    @staticmethod
    def get_help_action_at(position: tuple[int, int]) -> str | None:
        """Permite cerrar la ayuda mediante su botón superior."""

        if HELP_CLOSE_BUTTON.collidepoint(position):
            return "CERRAR"
        return None

    @staticmethod
    def get_information_action_at(position: tuple[int, int]) -> str | None:
        """Identifica enlaces y cierre de Créditos o Contacto."""

        controls = (
            ("CERRAR", INFO_CLOSE_BUTTON),
            ("LINKEDIN", LINKEDIN_BUTTON),
            ("GITHUB", GITHUB_BUTTON),
        )
        for action, control_rect in controls:
            if control_rect.collidepoint(position):
                return action
        return None

    @staticmethod
    def get_volume_from_position(position: tuple[int, int]) -> float:
        """Convierte la posición horizontal del deslizador en un porcentaje."""

        relative_x = position[0] - OPTIONS_SLIDER.left
        return min(1.0, max(0.0, relative_x / OPTIONS_SLIDER.width))

    @staticmethod
    def get_difficulty_at(position: tuple[int, int]) -> int | None:
        """Devuelve el índice de la tarjeta de dificultad pulsada."""

        for index, card_rect in enumerate(DIFFICULTY_CARDS):
            if card_rect.collidepoint(position):
                return index
        return None

    def _draw_input_box(
        self,
        typed_text: str,
        caret_visible: bool,
    ) -> None:
        """Muestra el texto introducido y el cursor parpadeante."""

        input_box = pygame.Rect(0, 0, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)
        input_box.center = (INPUT_BOX_CENTER_X, INPUT_BOX_CENTER_Y)

        pygame.draw.rect(
            self.screen,
            PANEL_COLOR,
            input_box,
            border_radius=12,
        )
        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR if typed_text else BORDER_COLOR,
            input_box,
            width=2,
            border_radius=12,
        )

        input_start_x = input_box.left + INPUT_HORIZONTAL_PADDING

        if typed_text:
            displayed_text = typed_text
            displayed_color = TEXT_COLOR
            text_x = input_start_x
        else:
            displayed_text = "Empieza a escribir..."
            displayed_color = MUTED_TEXT_COLOR
            text_x = input_start_x + 12

        text_surface = self.body_font.render(
            displayed_text,
            True,
            displayed_color,
        )
        text_rect = text_surface.get_rect(
            midleft=(text_x, input_box.centery)
        )
        self.screen.blit(text_surface, text_rect)

        # El cursor sigue el final del texto o espera al inicio si está vacío.
        caret_x = text_rect.right + 3 if typed_text else input_start_x

        if caret_visible:
            caret_rect = pygame.Rect(caret_x, 0, CARET_WIDTH, CARET_HEIGHT)
            caret_rect.centery = input_box.centery
            pygame.draw.rect(
                self.screen,
                ACCENT_COLOR,
                caret_rect,
                border_radius=2,
            )

    def _draw_top_hud(
        self,
        score: int,
        lives: int,
        wave_manager: WaveManager,
    ) -> None:
        """Agrupa título, puntuación, oleada y vidas en la zona superior."""

        typing_surface = self.body_font.render("TYPING", True, TEXT_COLOR)
        survivor_surface = self.body_font.render(
            "SURVIVOR",
            True,
            ACCENT_COLOR,
        )
        self.screen.blit(typing_surface, (HUD_PANEL_MARGIN + 8, 28))
        self.screen.blit(survivor_surface, (HUD_PANEL_MARGIN + 8, 57))

        # Las tarjetas ocupan solo el ancho necesario para sus datos actuales.
        panel_top = TOP_HUD_TOP + 8
        panel_height = 58
        score_panel = pygame.Rect(205, panel_top, 112, panel_height)
        wave_panel = pygame.Rect(329, panel_top, 154, panel_height)
        self._draw_panel(score_panel)
        self._draw_panel(wave_panel)

        self._draw_top_value_panel(
            score_panel,
            "PUNTOS",
            str(score),
        )
        self._draw_top_value_panel(
            wave_panel,
            "OLEADA",
            str(wave_manager.current_wave),
            (
                f"PROGRESO {wave_manager.completed_words_in_wave}"
                f"/{WORDS_PER_WAVE}"
            ),
        )
        self._draw_lives(lives)

    def _draw_top_value_panel(
        self,
        panel_rect: pygame.Rect,
        label: str,
        value: str,
        detail: str | None = None,
    ) -> None:
        """Dibuja una tarjeta superior con un valor y su información secundaria."""

        label_surface = self.small_font.render(label, True, ACCENT_COLOR)
        self.screen.blit(label_surface, (panel_rect.left + 12, panel_rect.top + 6))

        value_surface = self.body_font.render(value, True, TEXT_COLOR)
        value_rect = value_surface.get_rect(
            bottomleft=(panel_rect.left + 12, panel_rect.bottom - 7)
        )
        self.screen.blit(value_surface, value_rect)

        if detail is not None:
            detail_surface = self.small_font.render(
                detail,
                True,
                MUTED_TEXT_COLOR,
            )
            detail_rect = detail_surface.get_rect(
                bottomright=(panel_rect.right - 10, panel_rect.bottom - 8)
            )
            self.screen.blit(detail_surface, detail_rect)

    def _draw_lives(self, lives: int) -> None:
        """Representa las vidas como corazones llenos o vacíos."""

        for life_index in range(STARTING_LIVES):
            self._draw_heart_icon(
                center=(
                    1140 + life_index * 48,
                    TOP_HUD_TOP + TOP_HUD_HEIGHT // 2,
                ),
                filled=life_index < lives,
            )

    def _draw_heart_icon(
        self,
        center: tuple[int, int],
        filled: bool,
    ) -> None:
        """Dibuja un corazón geométrico sin depender de una fuente especial."""

        center_x, center_y = center
        outer_color = ENEMY_OUTLINE_COLOR if filled else BORDER_COLOR
        inner_color = INCORRECT_COLOR if filled else BACKGROUND_COLOR

        pygame.draw.circle(
            self.screen,
            outer_color,
            (center_x - 8, center_y - 6),
            12,
        )
        pygame.draw.circle(
            self.screen,
            outer_color,
            (center_x + 8, center_y - 6),
            12,
        )
        pygame.draw.polygon(
            self.screen,
            outer_color,
            (
                (center_x - 19, center_y - 3),
                (center_x + 19, center_y - 3),
                (center_x, center_y + 22),
            ),
        )
        pygame.draw.circle(
            self.screen,
            inner_color,
            (center_x - 7, center_y - 5),
            8,
        )
        pygame.draw.circle(
            self.screen,
            inner_color,
            (center_x + 7, center_y - 5),
            8,
        )
        pygame.draw.polygon(
            self.screen,
            inner_color,
            (
                (center_x - 14, center_y - 2),
                (center_x + 14, center_y - 2),
                (center_x, center_y + 16),
            ),
        )

    def _draw_bottom_hud(
        self,
        typed_text: str,
        caret_visible: bool,
        combo: int,
        combo_multiplier: int,
        combo_progress: float,
        typing_stats: TypingStats,
        slow_charge_available: bool,
        slow_time_remaining: float,
    ) -> None:
        """Dibuja una barra inferior compacta con acciones y métricas."""

        bottom_panel = pygame.Rect(
            HUD_PANEL_MARGIN,
            BOTTOM_HUD_TOP,
            WINDOW_WIDTH - HUD_PANEL_MARGIN * 2,
            BOTTOM_HUD_HEIGHT,
        )
        self._draw_panel(bottom_panel)

        for separator_x in (130, 265, 395, 855):
            pygame.draw.line(
                self.screen,
                BORDER_COLOR,
                (separator_x, bottom_panel.top + 16),
                (separator_x, bottom_panel.bottom - 16),
                width=2,
            )

        self._draw_bottom_metric(
            "PPM",
            f"{typing_stats.words_per_minute:.0f}",
            43,
        )
        self._draw_bottom_metric(
            "PRECISIÓN",
            f"{typing_stats.accuracy:.0f}%",
            148,
        )
        self._draw_bottom_metric(
            f"COMBO {combo}",
            f"x{combo_multiplier}",
            283,
            ACCENT_COLOR,
        )
        self._draw_combo_progress(combo_multiplier, combo_progress)
        self._draw_input_box(typed_text, caret_visible)
        self._draw_power_up_slots(
            slow_charge_available,
            slow_time_remaining,
        )

    def _draw_bottom_metric(
        self,
        label: str,
        value: str,
        x: int,
        value_color: tuple[int, int, int] = TEXT_COLOR,
    ) -> None:
        """Dibuja una métrica compacta en la barra inferior."""

        label_surface = self.small_font.render(label, True, MUTED_TEXT_COLOR)
        value_surface = self.body_font.render(value, True, value_color)
        self.screen.blit(label_surface, (x, BOTTOM_HUD_TOP + 17))
        self.screen.blit(value_surface, (x, BOTTOM_HUD_TOP + 44))

    def _draw_combo_progress(
        self,
        combo_multiplier: int,
        combo_progress: float,
    ) -> None:
        """Muestra el avance del combo dentro de su sección del HUD."""

        bar_rect = pygame.Rect(
            283,
            BOTTOM_HUD_TOP + 84,
            COMBO_BAR_WIDTH,
            COMBO_BAR_HEIGHT,
        )
        pygame.draw.rect(
            self.screen,
            BACKGROUND_COLOR,
            bar_rect,
            border_radius=4,
        )
        pygame.draw.rect(
            self.screen,
            BORDER_COLOR,
            bar_rect,
            width=1,
            border_radius=4,
        )

        progress = (
            1.0
            if combo_multiplier >= MAX_COMBO_MULTIPLIER
            else max(0.0, min(1.0, combo_progress))
        )
        fill_width = round((COMBO_BAR_WIDTH - 4) * progress)

        if fill_width > 0:
            fill_rect = pygame.Rect(
                bar_rect.left + 2,
                bar_rect.top + 2,
                fill_width,
                COMBO_BAR_HEIGHT - 4,
            )
            pygame.draw.rect(
                self.screen,
                ACCENT_COLOR,
                fill_rect,
                border_radius=2,
            )

    def _draw_power_up_slots(
        self,
        slow_charge_available: bool,
        slow_time_remaining: float,
    ) -> None:
        """Alinea las seis ranuras de power-ups en la barra inferior."""

        slots_width = (
            POWER_UP_SLOT_SIZE * 6
            + POWER_UP_SLOT_GAP * 5
        )
        first_slot_left = 880
        slot_top = BOTTOM_HUD_TOP + 40

        title_surface = self.small_font.render(
            "POTENCIADORES",
            True,
            MUTED_TEXT_COLOR,
        )
        title_rect = title_surface.get_rect(
            center=(first_slot_left + slots_width // 2, BOTTOM_HUD_TOP + 20)
        )
        self.screen.blit(title_surface, title_rect)

        for slot_index in range(6):
            slot_rect = pygame.Rect(
                first_slot_left
                + slot_index * (POWER_UP_SLOT_SIZE + POWER_UP_SLOT_GAP),
                slot_top,
                POWER_UP_SLOT_SIZE,
                POWER_UP_SLOT_SIZE,
            )
            slot_color = (
                POWER_UP_COLOR
                if slot_index == 0
                and (slow_charge_available or slow_time_remaining > 0.0)
                else BORDER_COLOR
            )
            pygame.draw.rect(
                self.screen,
                BACKGROUND_COLOR,
                slot_rect,
                border_radius=8,
            )
            pygame.draw.rect(
                self.screen,
                slot_color,
                slot_rect,
                width=2,
                border_radius=8,
            )

            key_surface = self.small_font.render(
                str(slot_index + 1),
                True,
                slot_color,
            )
            self.screen.blit(
                key_surface,
                (slot_rect.left + 5, slot_rect.top + 2),
            )

            if slot_index == 0:
                self._draw_slow_power_up_icon(
                    slot_rect,
                    slow_charge_available,
                    slow_time_remaining,
                )

    def _draw_slow_power_up_icon(
        self,
        slot_rect: pygame.Rect,
        slow_charge_available: bool,
        slow_time_remaining: float,
    ) -> None:
        """Representa provisionalmente la ralentización como un reloj."""

        is_available = slow_charge_available or slow_time_remaining > 0.0
        icon_color = POWER_UP_COLOR if is_available else MUTED_TEXT_COLOR
        icon_center = slot_rect.center
        icon_radius = 18

        pygame.draw.circle(
            self.screen,
            icon_color,
            icon_center,
            icon_radius,
            width=3,
        )
        pygame.draw.line(
            self.screen,
            icon_color,
            icon_center,
            (icon_center[0], icon_center[1] - 10),
            width=3,
        )
        pygame.draw.line(
            self.screen,
            icon_color,
            icon_center,
            (icon_center[0] + 8, icon_center[1] + 5),
            width=3,
        )

        if slow_time_remaining <= 0.0:
            return

        duration_ratio = min(
            1.0,
            slow_time_remaining / SLOW_POWER_UP_DURATION,
        )
        duration_bar = pygame.Rect(
            slot_rect.left + 8,
            slot_rect.bottom - 9,
            round((POWER_UP_SLOT_SIZE - 16) * duration_ratio),
            4,
        )
        pygame.draw.rect(
            self.screen,
            POWER_UP_COLOR,
            duration_bar,
            border_radius=2,
        )

    def _draw_panel(self, panel_rect: pygame.Rect) -> None:
        """Dibuja un panel reutilizable con el estilo general del HUD."""

        pygame.draw.rect(
            self.screen,
            PANEL_COLOR,
            panel_rect,
            border_radius=12,
        )
        pygame.draw.rect(
            self.screen,
            BORDER_COLOR,
            panel_rect,
            width=2,
            border_radius=12,
        )

    def _draw_game_over(
        self,
        high_score: HighScore,
        is_new_high_score: bool,
        score: int,
        completed_words: int,
        wave_manager: WaveManager,
        defeated_enemies: Counter[EnemyType],
        typing_stats: TypingStats,
    ) -> None:
        """Dibuja la capa de derrota y el resultado de la partida."""

        self._draw_overlay()

        game_over_surface = self.title_font.render(
            "NUEVO RÉCORD" if is_new_high_score else "FIN DE LA PARTIDA",
            True,
            ACCENT_COLOR if is_new_high_score else INCORRECT_COLOR,
        )
        game_over_rect = game_over_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 55)
        )
        self.screen.blit(game_over_surface, game_over_rect)

        result_surface = self.body_font.render(
            f"Puntuación: {score}  |  Récord: {high_score.score}",
            True,
            TEXT_COLOR,
        )
        result_rect = result_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
        )
        self.screen.blit(result_surface, result_rect)

        session_surface = self.small_font.render(
            (
                f"Palabras: {completed_words}"
                f"  |  Oleada: {wave_manager.current_wave}"
            ),
            True,
            MUTED_TEXT_COLOR,
        )
        session_rect = session_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 45)
        )
        self.screen.blit(session_surface, session_rect)

        defeated_surface = self.small_font.render(
            (
                "Eliminados  |  "
                f"{self._get_enemy_defeat_summary(defeated_enemies)}"
            ),
            True,
            MUTED_TEXT_COLOR,
        )
        defeated_rect = defeated_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80)
        )
        self.screen.blit(defeated_surface, defeated_rect)

        stats_surface = self.small_font.render(
            (
                f"PPM: {typing_stats.words_per_minute:.1f}"
                f"  |  Precisión: {typing_stats.accuracy:.1f}%"
                f"  |  Errores: {typing_stats.errors}"
            ),
            True,
            MUTED_TEXT_COLOR,
        )
        stats_rect = stats_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 115)
        )
        self.screen.blit(stats_surface, stats_rect)

        restart_surface = self.small_font.render(
            "R: reiniciar  |  H: ayuda y opciones  |  Esc: cerrar",
            True,
            MUTED_TEXT_COLOR,
        )
        restart_rect = restart_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 155)
        )
        self.screen.blit(restart_surface, restart_rect)

    def _draw_menu(self, high_score: HighScore, selection: int) -> None:
        """Dibuja la portada y sus accesos principales."""

        self._draw_overlay(alpha=188)

        menu_title = self.title_font.render(
            "TYPING SURVIVOR",
            True,
            ACCENT_COLOR,
        )
        self.screen.blit(
            menu_title,
            menu_title.get_rect(center=(WINDOW_WIDTH // 2, 82)),
        )

        subtitle = self.small_font.render(
            "ESCRIBE. RESISTE. SOBREVIVE.",
            True,
            TEXT_COLOR,
        )
        self.screen.blit(
            subtitle,
            subtitle.get_rect(center=(WINDOW_WIDTH // 2, 128)),
        )

        record_surface = self.small_font.render(
            (
                f"RÉCORD  {high_score.score} PTS"
                f"  ·  OLEADA {high_score.wave}"
                f"  ·  {high_score.words_per_minute:.1f} PPM"
                f"  ·  {high_score.accuracy:.1f}%"
            ),
            True,
            MUTED_TEXT_COLOR,
        )
        self.screen.blit(
            record_surface,
            record_surface.get_rect(center=(WINDOW_WIDTH // 2, 174)),
        )

        for index, (label, button_rect) in enumerate(
            zip(MAIN_MENU_ACTIONS[:4], MAIN_MENU_BUTTONS)
        ):
            self._draw_menu_button(
                button_rect,
                label,
                selected=index == selection,
            )

        self._draw_small_menu_button(
            MENU_CREDITS_BUTTON,
            "CRÉDITOS",
            selected=selection == 4,
        )
        self._draw_small_menu_button(
            MENU_CONTACT_BUTTON,
            "CONTACTO",
            selected=selection == 5,
        )

        navigation = self.small_font.render(
            "Arriba / Abajo: seleccionar  ·  Enter: confirmar",
            True,
            MUTED_TEXT_COLOR,
        )
        self.screen.blit(
            navigation,
            navigation.get_rect(center=(WINDOW_WIDTH // 2, 665)),
        )

    def _draw_difficulty(self, selection: int) -> None:
        """Muestra las tres dificultades antes de iniciar la ronda."""

        self._draw_overlay(alpha=205)

        title = self.title_font.render(
            "ELIGE LA DIFICULTAD",
            True,
            ACCENT_COLOR,
        )
        self.screen.blit(
            title,
            title.get_rect(center=(WINDOW_WIDTH // 2, 105)),
        )

        subtitle = self.small_font.render(
            "La dificultad modifica la velocidad y el ritmo de aparición.",
            True,
            MUTED_TEXT_COLOR,
        )
        self.screen.blit(
            subtitle,
            subtitle.get_rect(center=(WINDOW_WIDTH // 2, 155)),
        )

        for index, (difficulty, card_rect) in enumerate(
            zip(Difficulty, DIFFICULTY_CARDS)
        ):
            selected = index == selection
            pygame.draw.rect(
                self.screen,
                PANEL_COLOR,
                card_rect,
                border_radius=16,
            )
            pygame.draw.rect(
                self.screen,
                ACCENT_COLOR if selected else BORDER_COLOR,
                card_rect,
                width=4 if selected else 2,
                border_radius=16,
            )

            label = self.body_font.render(
                difficulty.display_name,
                True,
                ACCENT_COLOR if selected else TEXT_COLOR,
            )
            self.screen.blit(
                label,
                label.get_rect(center=(card_rect.centerx, card_rect.top + 52)),
            )
            self._draw_wrapped_centered_text(
                difficulty.description,
                card_rect.centerx,
                card_rect.top + 105,
                card_rect.width - 48,
                MUTED_TEXT_COLOR,
            )

            status = self.small_font.render(
                "SELECCIONADA" if selected else "",
                True,
                ACCENT_COLOR,
            )
            self.screen.blit(
                status,
                status.get_rect(center=(card_rect.centerx, card_rect.bottom - 35)),
            )

        hint = self.small_font.render(
            "Izquierda / Derecha: seleccionar  ·  Enter: jugar  ·  Esc: volver",
            True,
            MUTED_TEXT_COLOR,
        )
        self.screen.blit(
            hint,
            hint.get_rect(center=(WINDOW_WIDTH // 2, 610)),
        )

    def _draw_options(
        self,
        audio_volume: float,
        audio_muted: bool,
        is_fullscreen: bool,
    ) -> None:
        """Presenta los ajustes disponibles desde la pantalla inicial."""

        self._draw_overlay(alpha=205)
        self._draw_panel(OPTIONS_PANEL)
        self._draw_close_button(OPTIONS_CLOSE_BUTTON)

        title = self.title_font.render("OPCIONES", True, ACCENT_COLOR)
        self.screen.blit(
            title,
            title.get_rect(center=(WINDOW_WIDTH // 2, 175)),
        )

        volume_label = (
            "VOLUMEN: SILENCIADO"
            if audio_muted
            else f"VOLUMEN: {round(audio_volume * 100)}%"
        )
        volume = self.body_font.render(volume_label, True, TEXT_COLOR)
        self.screen.blit(
            volume,
            volume.get_rect(center=(WINDOW_WIDTH // 2, 270)),
        )

        pygame.draw.rect(
            self.screen,
            BACKGROUND_COLOR,
            OPTIONS_SLIDER,
            border_radius=9,
        )
        pygame.draw.rect(
            self.screen,
            BORDER_COLOR,
            OPTIONS_SLIDER,
            width=2,
            border_radius=9,
        )
        filled_width = round((OPTIONS_SLIDER.width - 4) * audio_volume)
        if filled_width:
            filled = pygame.Rect(
                OPTIONS_SLIDER.left + 2,
                OPTIONS_SLIDER.top + 2,
                filled_width,
                OPTIONS_SLIDER.height - 4,
            )
            pygame.draw.rect(
                self.screen,
                MUTED_TEXT_COLOR if audio_muted else ACCENT_COLOR,
                filled,
                border_radius=6,
            )

        knob_x = OPTIONS_SLIDER.left + round(
            OPTIONS_SLIDER.width * audio_volume
        )
        pygame.draw.circle(
            self.screen,
            MUTED_TEXT_COLOR if audio_muted else ACCENT_COLOR,
            (knob_x, OPTIONS_SLIDER.centery),
            10,
        )

        fullscreen_text = (
            "PANTALLA COMPLETA: ACTIVADA"
            if is_fullscreen
            else "PANTALLA COMPLETA: DESACTIVADA"
        )
        self._draw_menu_button(
            OPTIONS_MUTE_BUTTON,
            "ACTIVAR SONIDO" if audio_muted else "SILENCIAR",
            selected=audio_muted,
            compact=True,
        )
        self._draw_menu_button(
            OPTIONS_FULLSCREEN_BUTTON,
            "SALIR DE PANTALLA" if is_fullscreen else "PANTALLA COMPLETA",
            selected=is_fullscreen,
            compact=True,
        )

        controls = self.small_font.render(
            fullscreen_text,
            True,
            MUTED_TEXT_COLOR,
        )
        self.screen.blit(
            controls,
            controls.get_rect(center=(WINDOW_WIDTH // 2, 465)),
        )
        self._draw_back_hint()

    def _draw_information_screen(
        self,
        title_text: str,
        lines: tuple[str, ...],
    ) -> None:
        """Dibuja una página informativa sencilla desde el menú."""

        self._draw_overlay(alpha=205)
        panel = pygame.Rect(WINDOW_WIDTH // 2 - 380, 145, 760, 390)
        self._draw_panel(panel)
        self._draw_close_button(INFO_CLOSE_BUTTON)

        title = self.title_font.render(title_text, True, ACCENT_COLOR)
        self.screen.blit(
            title,
            title.get_rect(center=(WINDOW_WIDTH // 2, 215)),
        )

        line_y = 285
        for line in lines:
            surface = self.body_font.render(line, True, TEXT_COLOR)
            self.screen.blit(
                surface,
                surface.get_rect(center=(WINDOW_WIDTH // 2, line_y)),
            )
            line_y += 55

        self._draw_menu_button(
            LINKEDIN_BUTTON,
            "LINKEDIN",
            selected=False,
        )
        self._draw_menu_button(
            GITHUB_BUTTON,
            "GITHUB",
            selected=False,
        )

        self._draw_back_hint()

    def _draw_menu_button(
        self,
        button_rect: pygame.Rect,
        label: str,
        selected: bool,
        compact: bool = False,
    ) -> None:
        """Dibuja un botón grande con un foco visible para teclado."""

        pygame.draw.rect(
            self.screen,
            PANEL_COLOR,
            button_rect,
            border_radius=12,
        )
        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR if selected else BORDER_COLOR,
            button_rect,
            width=3 if selected else 2,
            border_radius=12,
        )
        label_font = self.small_font if compact else self.body_font
        label_surface = label_font.render(
            label,
            True,
            ACCENT_COLOR if selected else TEXT_COLOR,
        )
        self.screen.blit(
            label_surface,
            label_surface.get_rect(center=button_rect.center),
        )

    def _draw_small_menu_button(
        self,
        button_rect: pygame.Rect,
        label: str,
        selected: bool,
    ) -> None:
        """Dibuja los accesos secundarios del pie de portada."""

        pygame.draw.rect(
            self.screen,
            PANEL_COLOR,
            button_rect,
            border_radius=8,
        )
        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR if selected else BORDER_COLOR,
            button_rect,
            width=2,
            border_radius=8,
        )
        label_surface = self.small_font.render(
            label,
            True,
            ACCENT_COLOR if selected else MUTED_TEXT_COLOR,
        )
        self.screen.blit(
            label_surface,
            label_surface.get_rect(center=button_rect.center),
        )

    def _draw_close_button(self, button_rect: pygame.Rect) -> None:
        """Dibuja un cierre visible y pulsable en una pantalla secundaria."""

        pygame.draw.rect(
            self.screen,
            BACKGROUND_COLOR,
            button_rect,
            border_radius=8,
        )
        pygame.draw.rect(
            self.screen,
            BORDER_COLOR,
            button_rect,
            width=2,
            border_radius=8,
        )
        close_surface = self.body_font.render("X", True, TEXT_COLOR)
        self.screen.blit(
            close_surface,
            close_surface.get_rect(center=button_rect.center),
        )

    def _draw_wrapped_centered_text(
        self,
        text: str,
        center_x: int,
        start_y: int,
        max_width: int,
        color: tuple[int, int, int],
    ) -> None:
        """Parte una descripción breve sin depender de una fuente externa."""

        lines: list[str] = []
        current_line = ""
        for word in text.split():
            candidate = f"{current_line} {word}".strip()
            if self.small_font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        for index, line in enumerate(lines):
            surface = self.small_font.render(line, True, color)
            self.screen.blit(
                surface,
                surface.get_rect(center=(center_x, start_y + index * 27)),
            )

    def _draw_back_hint(self) -> None:
        """Muestra el control común para regresar a la portada."""

        back = self.small_font.render("Esc: volver", True, MUTED_TEXT_COLOR)
        self.screen.blit(
            back,
            back.get_rect(center=(WINDOW_WIDTH // 2, 635)),
        )

    def _draw_pause(self, audio_volume: float, audio_muted: bool) -> None:
        """Dibuja una capa de pausa sobre la partida congelada."""

        self._draw_overlay()

        pause_surface = self.title_font.render(
            "PAUSA",
            True,
            ACCENT_COLOR,
        )
        pause_rect = pause_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 120)
        )
        self.screen.blit(pause_surface, pause_rect)

        volume_text = (
            "SILENCIADO"
            if audio_muted
            else f"VOLUMEN: {round(audio_volume * 100)}%"
        )
        volume_surface = self.body_font.render(
            volume_text,
            True,
            MUTED_TEXT_COLOR if audio_muted else TEXT_COLOR,
        )
        volume_rect = volume_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 35)
        )
        self.screen.blit(volume_surface, volume_rect)

        # La barra ofrece una lectura visual inmediata del volumen elegido.
        bar_width = 320
        bar_height = 14
        bar_rect = pygame.Rect(0, 0, bar_width, bar_height)
        bar_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 15)
        pygame.draw.rect(
            self.screen,
            PANEL_COLOR,
            bar_rect,
            border_radius=bar_height // 2,
        )
        pygame.draw.rect(
            self.screen,
            BORDER_COLOR,
            bar_rect,
            width=2,
            border_radius=bar_height // 2,
        )

        filled_width = round((bar_width - 4) * audio_volume)

        if filled_width > 0:
            filled_rect = pygame.Rect(
                bar_rect.left + 2,
                bar_rect.top + 2,
                filled_width,
                bar_height - 4,
            )
            pygame.draw.rect(
                self.screen,
                MUTED_TEXT_COLOR if audio_muted else ACCENT_COLOR,
                filled_rect,
                border_radius=(bar_height - 4) // 2,
            )

        controls_surface = self.small_font.render(
            "Izquierda / Derecha: volumen  |  M: silenciar",
            True,
            MUTED_TEXT_COLOR,
        )
        controls_rect = controls_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 65)
        )
        self.screen.blit(controls_surface, controls_rect)

        help_surface = self.small_font.render(
            "H: ayuda y opciones",
            True,
            MUTED_TEXT_COLOR,
        )
        help_rect = help_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100)
        )
        self.screen.blit(help_surface, help_rect)

        continue_surface = self.small_font.render(
            "Esc: continuar",
            True,
            MUTED_TEXT_COLOR,
        )
        continue_rect = continue_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 135)
        )
        self.screen.blit(continue_surface, continue_rect)

    def _draw_help(self, is_fullscreen: bool) -> None:
        """Muestra los controles y las reglas de los enemigos."""

        self._draw_overlay()

        help_panel = pygame.Rect(60, 35, WINDOW_WIDTH - 120, WINDOW_HEIGHT - 70)
        self._draw_panel(help_panel)
        self._draw_close_button(HELP_CLOSE_BUTTON)

        title_surface = self.title_font.render(
            "AYUDA",
            True,
            ACCENT_COLOR,
        )
        title_rect = title_surface.get_rect(
            center=(WINDOW_WIDTH // 2, 85)
        )
        self.screen.blit(title_surface, title_rect)

        controls_panel = pygame.Rect(90, 130, 525, 500)
        enemies_panel = pygame.Rect(665, 130, 525, 500)
        self._draw_panel(controls_panel)
        self._draw_panel(enemies_panel)

        self._draw_controls_guide(controls_panel, is_fullscreen)
        self._draw_enemy_guide(enemies_panel)

        back_surface = self.small_font.render(
            "Esc: volver",
            True,
            MUTED_TEXT_COLOR,
        )
        back_rect = back_surface.get_rect(
            center=(WINDOW_WIDTH // 2, 655)
        )
        self.screen.blit(back_surface, back_rect)

    def _draw_controls_guide(
        self,
        panel_rect: pygame.Rect,
        is_fullscreen: bool,
    ) -> None:
        """Dibuja los controles de juego y accesos rápidos."""

        title_surface = self.body_font.render(
            "CONTROLES",
            True,
            TEXT_COLOR,
        )
        self.screen.blit(title_surface, (panel_rect.left + 28, 155))

        control_rows = (
            ("Primera letra", "Seleccionar enemigo"),
            ("Retroceso", "Borrar un carácter"),
            ("1 - 6", "Activar potenciadores"),
            ("Esc", "Pausar o volver"),
            ("H", "Abrir ayuda"),
        )
        row_y = 205

        for key_text, action_text in control_rows:
            self._draw_help_row(
                panel_rect.left + 28,
                row_y,
                key_text,
                action_text,
            )
            row_y += 42

        options_surface = self.body_font.render(
            "ACCESOS RÁPIDOS",
            True,
            TEXT_COLOR,
        )
        self.screen.blit(options_surface, (panel_rect.left + 28, 425))

        fullscreen_status = "ACTIVADA" if is_fullscreen else "DESACTIVADA"
        self._draw_help_row(
            panel_rect.left + 28,
            478,
            "F11",
            f"Pantalla completa: {fullscreen_status}",
        )
        self._draw_help_row(
            panel_rect.left + 28,
            520,
            "Pausa",
            "Volumen y silencio",
        )

    def _draw_help_row(
        self,
        x: int,
        y: int,
        key_text: str,
        description: str,
    ) -> None:
        """Dibuja una tecla destacada junto a la acción que realiza."""

        key_surface = self.small_font.render(key_text, True, ACCENT_COLOR)
        self.screen.blit(key_surface, (x, y))

        description_surface = self.small_font.render(
            description,
            True,
            MUTED_TEXT_COLOR,
        )
        self.screen.blit(description_surface, (x + 155, y))

    def _draw_enemy_guide(self, panel_rect: pygame.Rect) -> None:
        """Explica visualmente las tres variantes de enemigos."""

        title_surface = self.body_font.render(
            "ENEMIGOS",
            True,
            TEXT_COLOR,
        )
        self.screen.blit(title_surface, (panel_rect.left + 28, 155))

        enemy_rows = (
            (
                EnemyType.NORMAL,
                "Equilibrado",
                "Una palabra para eliminarlo",
            ),
            (
                EnemyType.FAST,
                "Más veloz · x2 puntos",
                "Una palabra para eliminarlo",
            ),
            (
                EnemyType.ARMORED,
                "Más lento · x2 puntos",
                f"Resiste {ARMORED_ENEMY_HEALTH} palabras",
            ),
        )

        for index, (enemy_type, summary, detail) in enumerate(enemy_rows):
            center = (panel_rect.left + 65, 235 + index * 130)
            self._draw_enemy_guide_icon(enemy_type, center)

            name_surface = self.small_font.render(
                enemy_type.display_name,
                True,
                self._get_enemy_guide_color(enemy_type),
            )
            self.screen.blit(name_surface, (panel_rect.left + 115, center[1] - 35))

            summary_surface = self.small_font.render(
                summary,
                True,
                TEXT_COLOR,
            )
            self.screen.blit(summary_surface, (panel_rect.left + 115, center[1] - 4))

            detail_surface = self.small_font.render(
                detail,
                True,
                MUTED_TEXT_COLOR,
            )
            self.screen.blit(detail_surface, (panel_rect.left + 115, center[1] + 25))

    def _draw_enemy_guide_icon(
        self,
        enemy_type: EnemyType,
        center: tuple[int, int],
    ) -> None:
        """Dibuja una versión reducida de la silueta de cada enemigo."""

        center_x, center_y = center
        radius = 24

        if enemy_type is EnemyType.NORMAL:
            pygame.draw.circle(
                self.screen,
                ENEMY_OUTLINE_COLOR,
                center,
                radius + 4,
            )
            pygame.draw.circle(self.screen, ENEMY_COLOR, center, radius)
            core_color = ENEMY_CORE_COLOR
        elif enemy_type is EnemyType.FAST:
            points = (
                (center_x + radius + 5, center_y),
                (center_x - radius, center_y - radius),
                (center_x - radius, center_y + radius),
            )
            pygame.draw.polygon(self.screen, FAST_ENEMY_OUTLINE_COLOR, points)
            inner_points = (
                (center_x + radius, center_y),
                (center_x - radius + 4, center_y - radius + 4),
                (center_x - radius + 4, center_y + radius - 4),
            )
            pygame.draw.polygon(self.screen, FAST_ENEMY_COLOR, inner_points)
            core_color = FAST_ENEMY_CORE_COLOR
        else:
            outline_points = tuple(
                (
                    center_x + round(math.cos(angle) * (radius + 4)),
                    center_y + round(math.sin(angle) * (radius + 4)),
                )
                for angle in (0, math.pi / 3, 2 * math.pi / 3, math.pi,
                              4 * math.pi / 3, 5 * math.pi / 3)
            )
            body_points = tuple(
                (
                    center_x + round(math.cos(angle) * radius),
                    center_y + round(math.sin(angle) * radius),
                )
                for angle in (0, math.pi / 3, 2 * math.pi / 3, math.pi,
                              4 * math.pi / 3, 5 * math.pi / 3)
            )
            pygame.draw.polygon(
                self.screen,
                ARMORED_ENEMY_OUTLINE_COLOR,
                outline_points,
            )
            pygame.draw.polygon(
                self.screen,
                ARMORED_ENEMY_COLOR,
                body_points,
            )
            core_color = ARMORED_ENEMY_CORE_COLOR

        pygame.draw.circle(self.screen, core_color, center, radius // 3)

    @staticmethod
    def _get_enemy_guide_color(enemy_type: EnemyType) -> tuple[int, int, int]:
        """Devuelve el color identificativo utilizado en la guía."""

        return {
            EnemyType.NORMAL: ENEMY_COLOR,
            EnemyType.FAST: FAST_ENEMY_COLOR,
            EnemyType.ARMORED: ARMORED_ENEMY_COLOR,
        }[enemy_type]

    def _draw_countdown(
        self,
        countdown_remaining: float,
        restarting: bool,
    ) -> None:
        """Muestra el tiempo de preparación antes de activar la partida."""

        # Al reiniciar, una capa más clara deja visible la reaparición invertida.
        self._draw_overlay(
            alpha=RESTART_OVERLAY_ALPHA if restarting else None
        )

        ready_surface = self.body_font.render(
            "PREPÁRATE",
            True,
            TEXT_COLOR,
        )
        ready_rect = ready_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 55)
        )
        self.screen.blit(ready_surface, ready_rect)

        # Ceil mantiene cada número visible durante aproximadamente un segundo.
        displayed_number = max(1, math.ceil(countdown_remaining))
        number_surface = self.title_font.render(
            str(displayed_number),
            True,
            ACCENT_COLOR,
        )
        number_rect = number_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        )
        self.screen.blit(number_surface, number_rect)

    def _draw_overlay(self, alpha: int | None = None) -> None:
        """Oscurece la partida para destacar una pantalla superpuesta."""

        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA,
        )
        overlay_color = GAME_OVER_OVERLAY_COLOR
        if alpha is not None:
            overlay_color = (*GAME_OVER_OVERLAY_COLOR[:3], alpha)
        overlay.fill(overlay_color)
        self.screen.blit(overlay, (0, 0))

    @staticmethod
    def _get_enemy_defeat_summary(
        defeated_enemies: Counter[EnemyType],
    ) -> str:
        """Construye el resumen de enemigos eliminados por tipo."""

        return "  |  ".join(
            (
                f"{enemy_type.plural_name}: "
                f"{defeated_enemies[enemy_type]}"
            )
            for enemy_type in EnemyType
        )
