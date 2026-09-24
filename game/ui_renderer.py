"""Representación visual de la interfaz y las pantallas del juego."""

from collections import Counter
import math
from pathlib import Path

import pygame

from game.difficulty import Difficulty
from game.enemy_type import EnemyType
from game.game_state import GameState
from game.power_up_assets import load_power_up_icon
from game.power_up_manager import PowerUpManager
from game.power_up_type import PowerUpType
from game.save_manager import HighScore
from game.talents import TALENTS
from game.settings import (
    ACCENT_COLOR,
    ARMORED_ENEMY_COLOR,
    ARMORED_ENEMY_CORE_COLOR,
    ARMORED_ENEMY_HEALTH,
    ARMORED_ENEMY_OUTLINE_COLOR,
    ARMORED_ENEMY_SCORE_MULTIPLIER,
    BACKGROUND_COLOR,
    BOSS_ENEMY_COLOR,
    BOSS_SCORE_MULTIPLIER,
    BOTTOM_HUD_HEIGHT,
    BOTTOM_HUD_TOP,
    BORDER_COLOR,
    CARET_HEIGHT,
    CARET_WIDTH,
    COMBO_BAR_HEIGHT,
    COMBO_BAR_WIDTH,
    DOUBLE_POINTS_DURATION,
    EMP_STUN_DURATION,
    ENEMY_COLOR,
    ENEMY_CORE_COLOR,
    ENEMY_OUTLINE_COLOR,
    FAST_ENEMY_COLOR,
    FAST_ENEMY_CORE_COLOR,
    FAST_ENEMY_OUTLINE_COLOR,
    FAST_ENEMY_SCORE_MULTIPLIER,
    GAME_OVER_OVERLAY_COLOR,
    GOBLIN_ENEMY_COLOR,
    GOBLIN_ENEMY_CORE_COLOR,
    GOBLIN_ENEMY_OUTLINE_COLOR,
    INCORRECT_COLOR,
    INPUT_BOX_CENTER_X,
    INPUT_BOX_CENTER_Y,
    INPUT_BOX_HEIGHT,
    INPUT_BOX_WIDTH,
    INPUT_HORIZONTAL_PADDING,
    HUD_PANEL_MARGIN,
    MAX_COMBO_MULTIPLIER,
    NECROMANCER_ENEMY_COLOR,
    NECROMANCER_ENEMY_CORE_COLOR,
    NECROMANCER_ENEMY_OUTLINE_COLOR,
    NECROMANCER_SCORE_MULTIPLIER,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
    POWER_UP_SLOT_GAP,
    POWER_UP_SLOT_SIZE,
    RESTART_OVERLAY_ALPHA,
    SLOW_POWER_UP_DURATION,
    SKELETON_ENEMY_COLOR,
    SKELETON_ENEMY_CORE_COLOR,
    SKELETON_ENEMY_OUTLINE_COLOR,
    SKELETON_SCORE_MULTIPLIER,
    TEXT_COLOR,
    TOP_HUD_HEIGHT,
    TOP_HUD_TOP,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from game.typing_stats import TypingStats
from game.wave_manager import WaveManager


MAIN_MENU_ACTIONS = (
    "JUGAR",
    "TIENDA",
    "OPCIONES",
    "AYUDA",
    "CRÉDITOS",
    "SALIR",
)
MAIN_MENU_BUTTONS = tuple(
    pygame.Rect(WINDOW_WIDTH // 2 - 175, 245 + index * 60, 350, 52)
    for index in range(len(MAIN_MENU_ACTIONS))
)
GAME_OVER_ACTIONS = ("REINICIAR", "TIENDA", "AYUDA", "OPCIONES", "SALIR")
GAME_OVER_PANEL = pygame.Rect(WINDOW_WIDTH // 2 - 400, 34, 800, 652)
GAME_OVER_BUTTONS = tuple(
    pygame.Rect(WINDOW_WIDTH // 2 - 175, 351 + index * 52, 350, 44)
    for index in range(len(GAME_OVER_ACTIONS))
)
SHOP_PANEL = pygame.Rect(52, 28, WINDOW_WIDTH - 104, WINDOW_HEIGHT - 56)
SHOP_CLOSE_BUTTON = pygame.Rect(SHOP_PANEL.right - 48, SHOP_PANEL.top + 16, 32, 32)
SHOP_CARDS = tuple(
    pygame.Rect(90 + (index % 2) * 560, 170 + (index // 2) * 108, 540, 98)
    for index in range(len(TALENTS))
)
DIFFICULTY_CARDS = tuple(
    pygame.Rect(WINDOW_WIDTH // 2 - 418 + index * 288, 278, 260, 124)
    for index in range(3)
)
OPTIONS_PANEL = pygame.Rect(WINDOW_WIDTH // 2 - 290, 170, 580, 380)
OPTIONS_CLOSE_BUTTON = pygame.Rect(
    OPTIONS_PANEL.right - 48, OPTIONS_PANEL.top + 16, 32, 32
)
OPTIONS_SLIDER = pygame.Rect(WINDOW_WIDTH // 2 - 190, 330, 380, 18)
OPTIONS_MUTE_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 - 225, 390, 215, 52)
OPTIONS_FULLSCREEN_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 + 10, 390, 215, 52)
PAUSE_PANEL = pygame.Rect(WINDOW_WIDTH // 2 - 270, 145, 540, 430)
PAUSE_CLOSE_BUTTON = pygame.Rect(PAUSE_PANEL.right - 48, PAUSE_PANEL.top + 16, 32, 32)
PAUSE_SLIDER = pygame.Rect(WINDOW_WIDTH // 2 - 170, 315, 340, 18)
PAUSE_MUTE_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 - 220, 370, 210, 52)
PAUSE_HELP_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 + 10, 370, 210, 52)
PAUSE_RESUME_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 - 135, 460, 270, 52)
HELP_CLOSE_BUTTON = pygame.Rect(1170, 50, 32, 32)
HELP_MENU_PANEL = pygame.Rect(WINDOW_WIDTH // 2 - 280, 130, 560, 460)
HELP_MENU_CLOSE_BUTTON = pygame.Rect(
    HELP_MENU_PANEL.right - 48, HELP_MENU_PANEL.top + 16, 32, 32
)
HELP_SECTION_ACTIONS = ("CONTROLES", "ENEMIGOS")
HELP_SECTION_BUTTONS = tuple(
    pygame.Rect(WINDOW_WIDTH // 2 - 170, 275 + index * 100, 340, 64)
    for index in range(2)
)
ENEMY_PORTRAITS_DIR = (
    Path(__file__).resolve().parent.parent / "assets" / "images" / "ui"
    / "enemy_portraits"
)
ENEMY_PORTRAIT_FILES = {
    EnemyType.NORMAL: "normal_enemy_portrait.png",
    EnemyType.FAST: "fast_enemy_portrait.png",
    EnemyType.ARMORED: "armored_enemy_portrait.png",
    EnemyType.GOBLIN: "goblin_enemy_portrait.png",
    EnemyType.NECROMANCER: "necromancer_enemy_portrait.png",
    EnemyType.SKELETON: "skeleton_enemy_portrait.png",
    EnemyType.BOSS: "remains_golem_portrait.png",
}
ENEMY_PORTRAIT_SIZE = 74
INFO_PANEL = pygame.Rect(WINDOW_WIDTH // 2 - 360, 155, 720, 410)
INFO_CLOSE_BUTTON = pygame.Rect(INFO_PANEL.right - 48, INFO_PANEL.top + 16, 32, 32)
LINKEDIN_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 - 246, 420, 236, 62)
GITHUB_BUTTON = pygame.Rect(WINDOW_WIDTH // 2 + 10, 420, 236, 62)
SOCIAL_ICONS_DIR = (
    Path(__file__).resolve().parent.parent / "assets" / "images" / "ui"
    / "social_icons"
)
LINKEDIN_BLUE = (10, 102, 194)
GITHUB_DARK = (36, 41, 47)
SOCIAL_ICON_SIZE = 32


class UIRenderer:
    """Dibuja el HUD, el campo de escritura y las capas de estado."""

    main_menu_actions = MAIN_MENU_ACTIONS
    game_over_actions = GAME_OVER_ACTIONS
    help_section_actions = HELP_SECTION_ACTIONS

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
        self.animation_time = 0.0
        self.enemy_portraits = self._load_enemy_portraits()
        self.social_icons = {}
        for name, filename in (
            ("LINKEDIN", "linkedin_in_white.png"),
            ("GITHUB", "github_mark_white.png"),
        ):
            path = SOCIAL_ICONS_DIR / filename
            if path.is_file():
                icon = pygame.image.load(str(path)).convert_alpha()
                self.social_icons[name] = pygame.transform.smoothscale(
                    icon, (SOCIAL_ICON_SIZE, SOCIAL_ICON_SIZE)
                )
        self.power_up_icons = {
            power_up: icon
            for power_up in PowerUpType
            if (icon := load_power_up_icon(power_up, 34)) is not None
        }
        self.dim_power_up_icons = {}
        for power_up, icon in self.power_up_icons.items():
            dim_icon = icon.copy()
            dim_icon.set_alpha(100)
            self.dim_power_up_icons[power_up] = dim_icon

    def update(self, delta_time: float) -> None:
        """Avanza el brillo de la barra de combo durante la partida."""

        self.animation_time += max(0.0, delta_time)

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
        power_up_manager: PowerUpManager,
        bonus_heart_active: bool,
        max_lives: int,
    ) -> None:
        """Dibuja la información de la partida y el campo de escritura."""

        self._draw_top_hud(
            score=score,
            lives=lives,
            wave_manager=wave_manager,
            bonus_heart_active=bonus_heart_active,
            max_lives=max_lives,
        )
        self._draw_bottom_hud(
            typed_text=typed_text,
            caret_visible=caret_visible,
            combo=combo,
            combo_multiplier=combo_multiplier,
            combo_progress=combo_progress,
            typing_stats=typing_stats,
            power_up_manager=power_up_manager,
        )
        self._draw_double_points_timer(power_up_manager)

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
        game_over_selection: int,
        difficulty_selection: int,
        help_page: str,
        help_selection: int,
        restarting: bool,
        shop_points: int,
        shop_levels: dict[str, int],
        shop_selection: int,
        shop_message: str,
    ) -> None:
        """Dibuja la pantalla superpuesta que corresponde al estado actual."""

        if state is GameState.MENU:
            self._draw_menu(high_score, menu_selection)
        elif state is GameState.SHOP:
            self._draw_shop(shop_points, shop_levels, shop_selection, shop_message)
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
            self._draw_help(is_fullscreen, help_page, help_selection)
        elif state is GameState.GAME_OVER:
            self._draw_game_over(
                high_score=high_score,
                is_new_high_score=is_new_high_score,
                score=score,
                completed_words=completed_words,
                wave_manager=wave_manager,
                defeated_enemies=defeated_enemies,
                typing_stats=typing_stats,
                selection=game_over_selection,
            )

    @staticmethod
    def get_menu_action_at(position: tuple[int, int]) -> str | None:
        """Devuelve la acción del botón principal situado bajo el puntero."""

        for action, button_rect in zip(MAIN_MENU_ACTIONS, MAIN_MENU_BUTTONS):
            if button_rect.collidepoint(position):
                return action
        return None

    @staticmethod
    def get_game_over_action_at(position: tuple[int, int]) -> str | None:
        """Devuelve la acción del botón de fin de partida pulsado."""

        for action, button_rect in zip(GAME_OVER_ACTIONS, GAME_OVER_BUTTONS):
            if button_rect.collidepoint(position):
                return action
        return None

    @staticmethod
    def get_shop_action_at(position: tuple[int, int]) -> int | str | None:
        """Devuelve el talento pulsado o el botón de cierre de la tienda."""

        if SHOP_CLOSE_BUTTON.collidepoint(position):
            return "CERRAR"
        for index, card in enumerate(SHOP_CARDS):
            if card.collidepoint(position):
                return index
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
    def get_pause_control_at(position: tuple[int, int]) -> str | None:
        """Identifica los controles clicables de la pausa."""

        controls = (
            ("CONTINUAR", PAUSE_CLOSE_BUTTON),
            ("VOLUMEN", PAUSE_SLIDER.inflate(0, 24)),
            ("MUTE", PAUSE_MUTE_BUTTON),
            ("AYUDA", PAUSE_HELP_BUTTON),
            ("CONTINUAR", PAUSE_RESUME_BUTTON),
        )
        for action, control_rect in controls:
            if control_rect.collidepoint(position):
                return action
        return None

    @staticmethod
    def get_help_action_at(
        position: tuple[int, int], help_page: str,
    ) -> str | None:
        """Identifica los botones visibles de la ayuda."""

        close_button = (
            HELP_MENU_CLOSE_BUTTON if help_page == "menu" else HELP_CLOSE_BUTTON
        )
        if close_button.collidepoint(position):
            return "CERRAR"
        if help_page != "menu":
            return None
        for action, button_rect in zip(HELP_SECTION_ACTIONS, HELP_SECTION_BUTTONS):
            if button_rect.collidepoint(position):
                return action
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
    def get_pause_volume_from_position(position: tuple[int, int]) -> float:
        """Convierte el deslizador de pausa en un volumen entre cero y uno."""

        relative_x = position[0] - PAUSE_SLIDER.left
        return min(1.0, max(0.0, relative_x / PAUSE_SLIDER.width))

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
            max_text_width = input_box.width - INPUT_HORIZONTAL_PADDING * 2 - 10
            if self.body_font.size(displayed_text)[0] > max_text_width:
                suffix = displayed_text
                while (
                    len(suffix) > 1
                    and self.body_font.size("…" + suffix)[0] > max_text_width
                ):
                    suffix = suffix[1:]
                displayed_text = "…" + suffix
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
        bonus_heart_active: bool,
        max_lives: int,
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
                f"{('JEFE' if wave_manager.is_boss_wave else 'BAJAS')} "
                f"{wave_manager.defeated_in_wave}/{wave_manager.required_kills}"
            ),
        )
        self._draw_lives(lives, bonus_heart_active, max_lives)

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

    def _draw_lives(
        self,
        lives: int,
        bonus_heart_active: bool,
        max_lives: int,
    ) -> None:
        """Representa las vidas máximas y el corazón verde temporal."""

        heart_gap = 44
        first_heart_x = 1100 - max(0, max_lives + int(bonus_heart_active) - 4) * heart_gap
        heart_y = TOP_HUD_TOP + TOP_HUD_HEIGHT // 2
        for life_index in range(max_lives):
            self._draw_heart_icon(
                center=(first_heart_x + life_index * heart_gap, heart_y),
                filled=life_index < lives,
            )

        if bonus_heart_active:
            self._draw_heart_icon(
                center=(first_heart_x + max_lives * heart_gap, heart_y),
                filled=True,
                fill_color=PowerUpType.RECOVERY.color,
                outline_color=(25, 105, 65),
            )

    def _draw_heart_icon(
        self,
        center: tuple[int, int],
        filled: bool,
        fill_color: tuple[int, int, int] = INCORRECT_COLOR,
        outline_color: tuple[int, int, int] = ENEMY_OUTLINE_COLOR,
    ) -> None:
        """Dibuja un corazón geométrico sin depender de una fuente especial."""

        center_x, center_y = center
        outer_color = outline_color if filled else BORDER_COLOR
        inner_color = fill_color if filled else BACKGROUND_COLOR

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
        power_up_manager: PowerUpManager,
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
        max_combo = combo_multiplier >= MAX_COMBO_MULTIPLIER
        glow = 0.5 + 0.5 * math.sin(self.animation_time * 5.2)
        combo_color = (
            (round(100 + 95 * glow), round(215 + 35 * glow), 255)
            if max_combo else ACCENT_COLOR
        )
        self._draw_bottom_metric(
            f"COMBO {combo}",
            f"x{combo_multiplier}",
            283,
            combo_color,
        )
        self._draw_combo_progress(combo_multiplier, combo_progress)
        self._draw_input_box(typed_text, caret_visible)
        self._draw_power_up_slots(power_up_manager)

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
        """Anima un reflejo sobre la carga y destaca el x5 completo."""

        max_combo = combo_multiplier >= MAX_COMBO_MULTIPLIER
        bar_rect = pygame.Rect(
            INPUT_BOX_CENTER_X - COMBO_BAR_WIDTH // 2,
            BOTTOM_HUD_TOP - COMBO_BAR_HEIGHT - 8,
            COMBO_BAR_WIDTH,
            COMBO_BAR_HEIGHT,
        )
        if max_combo:
            intensity = round(70 + 45 * (
                0.5 + 0.5 * math.sin(self.animation_time * 6.0)
            ))
            pygame.draw.rect(
                self.screen, (35, intensity, 185),
                bar_rect.inflate(6, 6), width=2, border_radius=6,
            )
        pygame.draw.rect(
            self.screen, BACKGROUND_COLOR, bar_rect, border_radius=5,
        )
        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR if max_combo else BORDER_COLOR,
            bar_rect, width=1, border_radius=5,
        )

        progress = (
            1.0 if max_combo
            else max(0.0, min(1.0, combo_progress))
        )
        fill_width = round((COMBO_BAR_WIDTH - 4) * progress)
        if fill_width <= 0:
            return

        fill_rect = pygame.Rect(
            bar_rect.left + 2, bar_rect.top + 2,
            fill_width, COMBO_BAR_HEIGHT - 4,
        )
        pygame.draw.rect(
            self.screen,
            (85, 225, 255) if max_combo else ACCENT_COLOR,
            fill_rect, border_radius=3,
        )
        # La franja luminosa recorre la parte ya cargada y nunca sale de ella.
        travel = (self.animation_time * (115 if max_combo else 75)) % (
            fill_width + 20
        ) - 10
        shine = pygame.Rect(
            fill_rect.left + round(travel), fill_rect.top,
            12, fill_rect.height,
        ).clip(fill_rect)
        if shine.width > 0:
            pygame.draw.rect(
                self.screen, (225, 250, 255), shine, border_radius=2,
            )
        if max_combo:
            for offset in (0.0, 0.36, 0.72):
                x = fill_rect.left + round(
                    (self.animation_time * 62 + offset * fill_width)
                    % fill_width
                )
                pygame.draw.circle(
                    self.screen, (245, 255, 255),
                    (x, fill_rect.centery), 2,
                )
            sparkle = 0.5 + 0.5 * math.sin(self.animation_time * 7)
            for x, y, radius in (
                (352, BOTTOM_HUD_TOP + 56, round(4 + 2 * sparkle)),
                (376, BOTTOM_HUD_TOP + 44, round(2 + sparkle)),
            ):
                pygame.draw.polygon(
                    self.screen, (185, 240, 255),
                    ((x, y - radius), (x + radius, y),
                     (x, y + radius), (x - radius, y)),
                )

    def _draw_double_points_timer(
        self,
        power_up_manager: PowerUpManager,
    ) -> None:
        """Muestra el tiempo de x2 sobre las cuatro ranuras manuales."""

        remaining = power_up_manager.double_points_time_remaining
        if remaining <= 0.0:
            return

        panel = pygame.Rect(876, BOTTOM_HUD_TOP - 52, 344, 42)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel, border_radius=9)
        pygame.draw.rect(
            self.screen, PowerUpType.DOUBLE_POINTS.color,
            panel, width=2, border_radius=9,
        )
        multiplier = self.body_font.render(
            "x2", True, PowerUpType.DOUBLE_POINTS.color
        )
        self.screen.blit(multiplier, multiplier.get_rect(center=(910, panel.centery)))

        bar = pygame.Rect(952, panel.centery - 5, 177, 10)
        pygame.draw.rect(self.screen, BACKGROUND_COLOR, bar, border_radius=5)
        progress = max(0.0, min(1.0, remaining / DOUBLE_POINTS_DURATION))
        fill_width = round(bar.width * progress)
        if fill_width:
            fill = pygame.Rect(bar.left, bar.top, fill_width, bar.height)
            pygame.draw.rect(
                self.screen, PowerUpType.DOUBLE_POINTS.color,
                fill, border_radius=5,
            )
        timer = self.small_font.render(f"{remaining:.1f}s", True, TEXT_COLOR)
        self.screen.blit(timer, timer.get_rect(center=(1174, panel.centery)))

    def _draw_power_up_slots(
        self,
        power_up_manager: PowerUpManager,
    ) -> None:
        """Muestra las cuatro habilidades manuales, su carga y duración."""

        manual_power_ups = tuple(
            power_up for power_up in PowerUpType
            if not power_up.is_automatic
        )
        slots_width = (
            POWER_UP_SLOT_SIZE * len(manual_power_ups)
            + POWER_UP_SLOT_GAP * (len(manual_power_ups) - 1)
        )
        slots_area_left = 855
        slots_area_right = WINDOW_WIDTH - HUD_PANEL_MARGIN
        first_slot_left = (
            slots_area_left + (slots_area_right - slots_area_left - slots_width) // 2
        )
        slot_top = BOTTOM_HUD_TOP + (BOTTOM_HUD_HEIGHT - POWER_UP_SLOT_SIZE) // 2

        for power_up in manual_power_ups:
            slot_rect = pygame.Rect(
                first_slot_left
                + power_up.slot_index * (POWER_UP_SLOT_SIZE + POWER_UP_SLOT_GAP),
                slot_top,
                POWER_UP_SLOT_SIZE,
                POWER_UP_SLOT_SIZE,
            )
            has_charge = power_up_manager.has_charge(power_up)
            is_active = power_up_manager.is_active(power_up)
            slot_color = power_up.color if has_charge or is_active else BORDER_COLOR
            icon_color = (
                power_up.color if has_charge or is_active else MUTED_TEXT_COLOR
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
                str(power_up.slot_index + 1),
                True,
                slot_color,
            )
            self.screen.blit(
                key_surface,
                (slot_rect.left + 5, slot_rect.top + 2),
            )
            self._draw_power_up_icon(slot_rect, power_up, icon_color)

            if is_active:
                pygame.draw.circle(
                    self.screen,
                    power_up.color,
                    (slot_rect.right - 7, slot_rect.top + 7),
                    4,
                )

            active_time = power_up_manager.get_active_time(power_up)
            duration = self._get_power_up_duration(power_up)
            if active_time > 0.0 and duration > 0.0:
                duration_ratio = min(1.0, active_time / duration)
                duration_bar = pygame.Rect(
                    slot_rect.left + 8,
                    slot_rect.bottom - 8,
                    round((POWER_UP_SLOT_SIZE - 16) * duration_ratio),
                    4,
                )
                pygame.draw.rect(
                    self.screen,
                    power_up.color,
                    duration_bar,
                    border_radius=2,
                )

    @staticmethod
    def _get_power_up_duration(power_up: PowerUpType) -> float:
        """Devuelve la duración total de las habilidades temporales."""

        if power_up is PowerUpType.SLOW:
            return SLOW_POWER_UP_DURATION
        if power_up is PowerUpType.EMP:
            return EMP_STUN_DURATION
        if power_up is PowerUpType.DOUBLE_POINTS:
            return DOUBLE_POINTS_DURATION
        return 0.0

    def _draw_power_up_icon(
        self,
        slot_rect: pygame.Rect,
        power_up: PowerUpType,
        color: tuple[int, int, int],
    ) -> None:
        """Muestra el icono correspondiente o un símbolo de respaldo."""

        icon = self.power_up_icons.get(power_up)
        if icon is not None:
            if color == MUTED_TEXT_COLOR:
                icon = self.dim_power_up_icons[power_up]
            self.screen.blit(
                icon,
                icon.get_rect(center=(slot_rect.centerx + 2, slot_rect.centery + 3)),
            )
            return

        center_x = slot_rect.centerx + 2
        center_y = slot_rect.centery + 3

        if power_up is PowerUpType.SLOW:
            pygame.draw.circle(
                self.screen,
                color,
                (center_x, center_y),
                15,
                width=3,
            )
            pygame.draw.line(
                self.screen,
                color,
                (center_x, center_y),
                (center_x, center_y - 9),
                width=3,
            )
            pygame.draw.line(
                self.screen,
                color,
                (center_x, center_y),
                (center_x + 7, center_y + 5),
                width=3,
            )
        elif power_up is PowerUpType.SHIELD:
            pygame.draw.polygon(
                self.screen,
                color,
                (
                    (center_x, center_y - 16),
                    (center_x + 14, center_y - 10),
                    (center_x + 11, center_y + 8),
                    (center_x, center_y + 17),
                    (center_x - 11, center_y + 8),
                    (center_x - 14, center_y - 10),
                ),
                width=3,
            )
        elif power_up is PowerUpType.EMP:
            for radius in (6, 12, 17):
                pygame.draw.circle(
                    self.screen,
                    color,
                    (center_x, center_y),
                    radius,
                    width=2,
                )
        elif power_up is PowerUpType.MULTISHOT:
            shot_centers = (
                (center_x - 10, center_y + 8),
                (center_x, center_y - 8),
                (center_x + 11, center_y + 6),
            )
            pygame.draw.lines(
                self.screen,
                color,
                False,
                shot_centers,
                width=2,
            )
            for shot_center in shot_centers:
                pygame.draw.circle(self.screen, color, shot_center, 5)
        elif power_up is PowerUpType.RECOVERY:
            pygame.draw.circle(
                self.screen,
                color,
                (center_x - 6, center_y - 4),
                8,
            )
            pygame.draw.circle(
                self.screen,
                color,
                (center_x + 6, center_y - 4),
                8,
            )
            pygame.draw.polygon(
                self.screen,
                color,
                (
                    (center_x - 13, center_y - 1),
                    (center_x + 13, center_y - 1),
                    (center_x, center_y + 15),
                ),
            )
        elif power_up is PowerUpType.DOUBLE_POINTS:
            label = self.small_font.render("x2", True, color)
            self.screen.blit(label, label.get_rect(center=(center_x, center_y)))

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
        selection: int,
    ) -> None:
        """Dibuja el resultado y las acciones de fin de partida."""

        self._draw_overlay()
        self._draw_panel(GAME_OVER_PANEL)

        game_over_surface = self.title_font.render(
            "GAME OVER",
            True,
            INCORRECT_COLOR,
        )
        game_over_rect = game_over_surface.get_rect(
            center=(WINDOW_WIDTH // 2, 91)
        )
        self.screen.blit(game_over_surface, game_over_rect)

        if is_new_high_score:
            record_badge = self.small_font.render(
                "NUEVO RÉCORD", True, ACCENT_COLOR
            )
            self.screen.blit(
                record_badge,
                record_badge.get_rect(center=(WINDOW_WIDTH // 2, 133)),
            )

        result_surface = self.body_font.render(
            f"Puntuación: {score}  |  Récord: {high_score.score}",
            True,
            TEXT_COLOR,
        )
        result_rect = result_surface.get_rect(
            center=(WINDOW_WIDTH // 2, 169)
        )
        self.screen.blit(result_surface, result_rect)

        session_surface = self.small_font.render(
            (
                f"Palabras: {completed_words}"
                f"  |  Oleada: {wave_manager.current_wave}"
                f"  |  +{score} PTS para la tienda"
            ),
            True,
            MUTED_TEXT_COLOR,
        )
        session_rect = session_surface.get_rect(
            center=(WINDOW_WIDTH // 2, 203)
        )
        self.screen.blit(session_surface, session_rect)

        enemy_types = list(EnemyType)
        for line_index in range(0, len(enemy_types), 3):
            summary = self._get_enemy_defeat_summary(
                defeated_enemies, enemy_types[line_index:line_index + 3]
            )
            prefix = "Eliminados  |  " if line_index == 0 else ""
            defeated_surface = self.small_font.render(
                prefix + summary, True, MUTED_TEXT_COLOR
            )
            defeated_rect = defeated_surface.get_rect(
                center=(
                    WINDOW_WIDTH // 2,
                    235 + line_index // 3 * 24,
                )
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
            center=(WINDOW_WIDTH // 2, 319)
        )
        self.screen.blit(stats_surface, stats_rect)

        for index, (label, button_rect) in enumerate(
            zip(GAME_OVER_ACTIONS, GAME_OVER_BUTTONS)
        ):
            self._draw_menu_button(
                button_rect, label, selected=index == selection, compact=True
            )

        navigation = self.small_font.render(
            "Arriba / Abajo: seleccionar  ·  Enter: confirmar  ·  Esc: salir",
            True,
            MUTED_TEXT_COLOR,
        )
        self.screen.blit(
            navigation,
            navigation.get_rect(center=(WINDOW_WIDTH // 2, 643)),
        )

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
            zip(MAIN_MENU_ACTIONS, MAIN_MENU_BUTTONS)
        ):
            self._draw_menu_button(
                button_rect,
                label,
                selected=index == selection,
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

    def _draw_shop(
        self,
        available_points: int,
        levels: dict[str, int],
        selection: int,
        message: str,
    ) -> None:
        """Muestra el saldo y las ocho compras permanentes."""

        self._draw_overlay(alpha=205)
        self._draw_panel(SHOP_PANEL)
        self._draw_close_button(SHOP_CLOSE_BUTTON)
        title = self.title_font.render("TIENDA", True, ACCENT_COLOR)
        self.screen.blit(
            title, title.get_rect(center=(WINDOW_WIDTH // 2, 78))
        )
        balance = self.body_font.render(
            f"PUNTOS DISPONIBLES: {available_points:,}".replace(",", "."),
            True, TEXT_COLOR,
        )
        self.screen.blit(
            balance, balance.get_rect(center=(WINDOW_WIDTH // 2, 130))
        )

        for index, (talent, card) in enumerate(zip(TALENTS, SHOP_CARDS)):
            level = levels.get(talent.key, 0)
            cost = talent.next_cost(level)
            selected = index == selection
            pygame.draw.rect(self.screen, BACKGROUND_COLOR, card, border_radius=12)
            pygame.draw.rect(
                self.screen,
                ACCENT_COLOR if selected else BORDER_COLOR,
                card, width=3 if selected else 2, border_radius=12,
            )

            name = self.body_font.render(
                talent.name, True, ACCENT_COLOR if selected else TEXT_COLOR
            )
            self.screen.blit(name, (card.left + 16, card.top + 9))
            level_text = (
                f"NIVEL {level}/{talent.max_level}"
                if talent.max_level > 1
                else ("ADQUIRIDO" if level else "NIVEL 0/1")
            )
            level_surface = self.small_font.render(
                level_text, True, MUTED_TEXT_COLOR
            )
            self.screen.blit(
                level_surface,
                level_surface.get_rect(topright=(card.right - 16, card.top + 13)),
            )
            description = talent.description
            if talent.key == "precision_pulse":
                duration = (1.0, 1.5, 2.0)[max(0, level - 1)]
                description = f"Palabra perfecta: enemigos lentos {duration:g} s."
            detail = self.small_font.render(description, True, MUTED_TEXT_COLOR)
            self.screen.blit(detail, (card.left + 16, card.top + 43))

            price_text = (
                "COMPRA COMPLETA"
                if cost is None else f"PRECIO: {cost:,} PTS".replace(",", ".")
            )
            price_color = (
                MUTED_TEXT_COLOR if cost is None
                else TEXT_COLOR if available_points >= cost
                else INCORRECT_COLOR
            )
            price = self.small_font.render(price_text, True, price_color)
            self.screen.blit(price, (card.left + 16, card.top + 72))

            buy_button = pygame.Rect(card.right - 128, card.top + 65, 110, 28)
            can_buy = cost is not None and available_points >= cost
            pygame.draw.rect(
                self.screen, ACCENT_COLOR if can_buy else PANEL_COLOR,
                buy_button, border_radius=7,
            )
            buy_label = self.small_font.render(
                "COMPRAR" if cost is not None else "MÁXIMO",
                True, BACKGROUND_COLOR if can_buy else MUTED_TEXT_COLOR,
            )
            self.screen.blit(
                buy_label, buy_label.get_rect(center=buy_button.center)
            )

        if message:
            feedback = self.small_font.render(
                message,
                True,
                ACCENT_COLOR if "COMPRADO" in message else INCORRECT_COLOR,
            )
            self.screen.blit(
                feedback, feedback.get_rect(center=(WINDOW_WIDTH // 2, 620))
            )
        hint = self.small_font.render(
            "Flechas: elegir  ·  Enter o clic: comprar  ·  Esc: volver",
            True, MUTED_TEXT_COLOR,
        )
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, 654)))

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
                label.get_rect(center=card_rect.center),
            )

        hint = self.small_font.render(
            "Izquierda / Derecha: seleccionar  ·  Enter: jugar  ·  Esc: volver",
            True,
            MUTED_TEXT_COLOR,
        )
        self.screen.blit(
            hint,
            hint.get_rect(center=(WINDOW_WIDTH // 2, 515)),
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
            title.get_rect(center=(WINDOW_WIDTH // 2, OPTIONS_PANEL.top + 60)),
        )

        volume_label = (
            "VOLUMEN: SILENCIADO"
            if audio_muted
            else f"VOLUMEN: {round(audio_volume * 100)}%"
        )
        volume = self.body_font.render(volume_label, True, TEXT_COLOR)
        self.screen.blit(
            volume,
            volume.get_rect(center=(WINDOW_WIDTH // 2, 290)),
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

        self._draw_back_hint(OPTIONS_PANEL.bottom - 36)

    def _draw_information_screen(
        self,
        title_text: str,
        lines: tuple[str, ...],
    ) -> None:
        """Dibuja una página informativa sencilla desde el menú."""

        self._draw_overlay(alpha=205)
        self._draw_panel(INFO_PANEL)
        self._draw_close_button(INFO_CLOSE_BUTTON)

        title = self.title_font.render(title_text, True, ACCENT_COLOR)
        self.screen.blit(
            title,
            title.get_rect(center=(WINDOW_WIDTH // 2, INFO_PANEL.top + 62)),
        )
        pygame.draw.line(
            self.screen,
            ACCENT_COLOR,
            (WINDOW_WIDTH // 2 - 90, INFO_PANEL.top + 112),
            (WINDOW_WIDTH // 2 + 90, INFO_PANEL.top + 112),
            2,
        )

        line_y = 290 + (3 - len(lines)) * 22
        for index, line in enumerate(lines):
            color = TEXT_COLOR if index == 0 else MUTED_TEXT_COLOR
            surface = self.body_font.render(line, True, color)
            self.screen.blit(
                surface,
                surface.get_rect(center=(WINDOW_WIDTH // 2, line_y)),
            )
            line_y += 40

        self._draw_social_button(LINKEDIN_BUTTON, "LINKEDIN", LINKEDIN_BLUE)
        self._draw_social_button(GITHUB_BUTTON, "GITHUB", GITHUB_DARK)
        self._draw_back_hint(INFO_PANEL.bottom - 25)

    def _draw_social_button(
        self, button_rect: pygame.Rect, label: str, color: tuple[int, int, int]
    ) -> None:
        """Dibuja un enlace social con su color y símbolo de marca."""

        pygame.draw.rect(self.screen, color, button_rect, border_radius=12)
        pygame.draw.rect(
            self.screen, (175, 221, 255) if label == "LINKEDIN" else (201, 209, 217),
            button_rect, width=2, border_radius=12,
        )
        label_surface = self.small_font.render(label, True, TEXT_COLOR)
        icon = self.social_icons.get(label)
        icon_width = icon.get_width() if icon is not None else 0
        gap = 12 if icon is not None else 0
        content_left = button_rect.centerx - (icon_width + gap + label_surface.get_width()) // 2
        if icon is not None:
            self.screen.blit(icon, icon.get_rect(midleft=(content_left, button_rect.centery)))
        self.screen.blit(
            label_surface,
            label_surface.get_rect(midleft=(content_left + icon_width + gap, button_rect.centery)),
        )

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

    def _draw_back_hint(self, center_y: int = 635) -> None:
        """Muestra el control común para regresar a la portada."""

        back = self.small_font.render("Esc: volver", True, MUTED_TEXT_COLOR)
        self.screen.blit(
            back,
            back.get_rect(center=(WINDOW_WIDTH // 2, center_y)),
        )

    def _draw_pause(self, audio_volume: float, audio_muted: bool) -> None:
        """Dibuja controles de pausa interactivos sobre la partida congelada."""

        self._draw_overlay()
        self._draw_panel(PAUSE_PANEL)
        self._draw_close_button(PAUSE_CLOSE_BUTTON)

        title = self.title_font.render("PAUSA", True, ACCENT_COLOR)
        self.screen.blit(
            title,
            title.get_rect(center=(WINDOW_WIDTH // 2, PAUSE_PANEL.top + 65)),
        )

        volume_label = (
            "VOLUMEN: SILENCIADO"
            if audio_muted
            else f"VOLUMEN: {round(audio_volume * 100)}%"
        )
        volume = self.body_font.render(volume_label, True, TEXT_COLOR)
        self.screen.blit(
            volume,
            volume.get_rect(center=(WINDOW_WIDTH // 2, 275)),
        )

        pygame.draw.rect(
            self.screen, BACKGROUND_COLOR, PAUSE_SLIDER, border_radius=9,
        )
        pygame.draw.rect(
            self.screen, BORDER_COLOR, PAUSE_SLIDER, width=2, border_radius=9,
        )
        filled_width = round((PAUSE_SLIDER.width - 4) * audio_volume)
        if filled_width:
            filled = pygame.Rect(
                PAUSE_SLIDER.left + 2,
                PAUSE_SLIDER.top + 2,
                filled_width,
                PAUSE_SLIDER.height - 4,
            )
            pygame.draw.rect(
                self.screen,
                MUTED_TEXT_COLOR if audio_muted else ACCENT_COLOR,
                filled,
                border_radius=6,
            )
        knob_x = PAUSE_SLIDER.left + round(PAUSE_SLIDER.width * audio_volume)
        pygame.draw.circle(
            self.screen,
            MUTED_TEXT_COLOR if audio_muted else ACCENT_COLOR,
            (knob_x, PAUSE_SLIDER.centery),
            10,
        )

        self._draw_menu_button(
            PAUSE_MUTE_BUTTON,
            "ACTIVAR SONIDO" if audio_muted else "SILENCIAR",
            selected=audio_muted,
            compact=True,
        )
        self._draw_menu_button(
            PAUSE_HELP_BUTTON, "AYUDA", selected=False, compact=True,
        )
        self._draw_menu_button(
            PAUSE_RESUME_BUTTON, "CONTINUAR", selected=True,
        )

        hint = self.small_font.render("Esc: continuar", True, MUTED_TEXT_COLOR)
        self.screen.blit(
            hint,
            hint.get_rect(center=(WINDOW_WIDTH // 2, PAUSE_PANEL.bottom - 30)),
        )

    def _draw_help(
        self, is_fullscreen: bool, help_page: str, selection: int,
    ) -> None:
        """Muestra el índice de ayuda o una de sus dos fichas."""

        self._draw_overlay()
        if help_page == "menu":
            self._draw_panel(HELP_MENU_PANEL)
            self._draw_close_button(HELP_MENU_CLOSE_BUTTON)
            title_y = HELP_MENU_PANEL.top + 70
            hint_y = HELP_MENU_PANEL.bottom - 52
        else:
            help_panel = pygame.Rect(60, 35, WINDOW_WIDTH - 120, WINDOW_HEIGHT - 70)
            self._draw_panel(help_panel)
            self._draw_close_button(HELP_CLOSE_BUTTON)
            title_y = 85
            hint_y = 655

        title_surface = self.title_font.render("AYUDA", True, ACCENT_COLOR)
        self.screen.blit(
            title_surface,
            title_surface.get_rect(center=(WINDOW_WIDTH // 2, title_y)),
        )

        if help_page == "menu":
            for index, (label, button_rect) in enumerate(
                zip(HELP_SECTION_ACTIONS, HELP_SECTION_BUTTONS)
            ):
                self._draw_menu_button(button_rect, label, index == selection)
            hint = "Arriba / Abajo: seleccionar  ·  Enter: abrir  ·  Esc: volver"
        else:
            content_panel = pygame.Rect(90, 135, WINDOW_WIDTH - 180, 495)
            self._draw_panel(content_panel)
            if help_page == "controls":
                self._draw_controls_guide(content_panel, is_fullscreen)
            else:
                self._draw_enemy_guide(content_panel)
            hint = "Esc: volver a ayuda"

        back_surface = self.small_font.render(hint, True, MUTED_TEXT_COLOR)
        self.screen.blit(
            back_surface,
            back_surface.get_rect(center=(WINDOW_WIDTH // 2, hint_y)),
        )

    def _draw_controls_guide(
        self,
        panel_rect: pygame.Rect,
        is_fullscreen: bool,
    ) -> None:
        """Reparte los controles de juego y de menú en dos columnas."""

        column_centers = (
            panel_rect.left + panel_rect.width // 4,
            panel_rect.left + 3 * panel_rect.width // 4,
        )
        for title, center_x in zip(
            ("CONTROLES", "ACCESOS RÁPIDOS"), column_centers
        ):
            title_surface = self.body_font.render(title, True, TEXT_COLOR)
            self.screen.blit(
                title_surface,
                title_surface.get_rect(center=(center_x, panel_rect.top + 44)),
            )

        control_rows = (
            ("Retroceso", "Borrar un carácter"),
            ("1 - 4", "Activar potenciadores"),
            ("Esc", "Pausar o volver"),
            ("H", "Abrir ayuda"),
        )
        fullscreen_status = "ACTIVADA" if is_fullscreen else "DESACTIVADA"
        shortcut_rows = (
            ("F11", f"Pantalla completa: {fullscreen_status}"),
            ("Pausa", "Volumen y silencio"),
            ("Arriba / Abajo", "Seleccionar en los menús"),
            ("Enter", "Confirmar selección"),
            ("Ratón", "Pulsar botones y controles"),
        )
        for rows, center_x in zip((control_rows, shortcut_rows), column_centers):
            key_width = max(self.small_font.size(key)[0] for key, _ in rows)
            description_width = max(
                self.small_font.size(description)[0]
                for _, description in rows
            )
            key_x = center_x - (key_width + 28 + description_width) // 2
            description_x = key_x + key_width + 28
            first_y = panel_rect.centery + 16 - (len(rows) - 1) * 34
            for index, (key_text, action_text) in enumerate(rows):
                self._draw_help_row(
                    key_x, description_x, first_y + index * 68,
                    key_text, action_text,
                )

    def _draw_help_row(
        self,
        key_x: int,
        description_x: int,
        y: int,
        key_text: str,
        description: str,
    ) -> None:
        """Dibuja una tecla destacada junto a la acción que realiza."""

        key_surface = self.small_font.render(key_text, True, ACCENT_COLOR)
        self.screen.blit(key_surface, (key_x, y))

        description_surface = self.small_font.render(
            description,
            True,
            MUTED_TEXT_COLOR,
        )
        self.screen.blit(description_surface, (description_x, y))

    def _draw_enemy_guide(self, panel_rect: pygame.Rect) -> None:
        """Explica visualmente los tipos de enemigos disponibles."""

        title_surface = self.body_font.render(
            "ENEMIGOS",
            True,
            TEXT_COLOR,
        )
        self.screen.blit(title_surface, (panel_rect.left + 30, panel_rect.top + 20))

        enemy_rows = (
            (
                EnemyType.NORMAL,
                "Equilibrado",
                "Una palabra para eliminarlo",
                1,
            ),
            (
                EnemyType.FAST,
                "Más veloz",
                "Una palabra para eliminarlo",
                FAST_ENEMY_SCORE_MULTIPLIER,
            ),
            (
                EnemyType.ARMORED,
                "Más lento",
                f"Resiste {ARMORED_ENEMY_HEALTH} palabras",
                ARMORED_ENEMY_SCORE_MULTIPLIER,
            ),
            (
                EnemyType.GOBLIN,
                "Cinco desvíos aleatorios",
                "Se acerca con cada movimiento",
                1,
            ),
            (
                EnemyType.NECROMANCER,
                "Inmóvil · invoca esqueletos",
                "6-7 letras · hasta 3 esqueletos",
                NECROMANCER_SCORE_MULTIPLIER,
            ),
            (
                EnemyType.SKELETON,
                "Palabras de tres letras",
                "Avanza desde el nigromante",
                SKELETON_SCORE_MULTIPLIER,
            ),
            (
                EnemyType.BOSS,
                "Inmóvil · invoca cada 1,5 segundos",
                "La ronda acaba al derrotarlo",
                BOSS_SCORE_MULTIPLIER,
            ),
        )

        for index, (enemy_type, summary, detail, score_multiplier) in enumerate(
            enemy_rows
        ):
            column = index // 4
            row = index % 4
            column_x = panel_rect.left + 30 + column * 540
            center = (column_x + 42, panel_rect.top + 95 + row * 105)
            text_x = column_x + 94
            self._draw_enemy_guide_icon(enemy_type, center)

            name_surface = self.small_font.render(
                enemy_type.display_name,
                True,
                self._get_enemy_guide_color(enemy_type),
            )
            self.screen.blit(name_surface, (text_x, center[1] - 24))

            summary_surface = self.small_font.render(summary, True, TEXT_COLOR)
            self.screen.blit(summary_surface, (text_x, center[1] - 1))

            detail_surface = self.small_font.render(
                detail, True, MUTED_TEXT_COLOR,
            )
            self.screen.blit(detail_surface, (text_x, center[1] + 21))

            multiplier_text = f"x{score_multiplier:g}".replace(".", ",")
            points_surface = self.small_font.render(
                f"Puntos por palabra: {multiplier_text}", True, ACCENT_COLOR
            )
            self.screen.blit(points_surface, (text_x, center[1] + 43))

    @staticmethod
    def _load_enemy_portraits() -> dict[EnemyType, pygame.Surface]:
        """Carga y ajusta los retratos sin deformar sus proporciones."""

        portraits = {}
        for enemy_type, filename in ENEMY_PORTRAIT_FILES.items():
            try:
                image = pygame.image.load(
                    str(ENEMY_PORTRAITS_DIR / filename)
                ).convert_alpha()
                visible = image.get_bounding_rect(min_alpha=8)
                if not visible:
                    continue
                image = image.subsurface(visible).copy()
                scale = min(
                    ENEMY_PORTRAIT_SIZE / image.get_width(),
                    ENEMY_PORTRAIT_SIZE / image.get_height(),
                )
                portraits[enemy_type] = pygame.transform.smoothscale(
                    image,
                    (
                        max(1, round(image.get_width() * scale)),
                        max(1, round(image.get_height() * scale)),
                    ),
                )
            except (pygame.error, OSError):
                continue
        return portraits

    def _draw_enemy_guide_icon(
        self,
        enemy_type: EnemyType,
        center: tuple[int, int],
    ) -> None:
        """Muestra el retrato del enemigo o su silueta de respaldo."""

        portrait = self.enemy_portraits.get(enemy_type)
        if portrait is not None:
            frame = pygame.Rect(0, 0, 84, 84)
            frame.center = center
            pygame.draw.rect(self.screen, BACKGROUND_COLOR, frame, border_radius=12)
            pygame.draw.rect(
                self.screen, BORDER_COLOR, frame, width=1, border_radius=12
            )
            self.screen.blit(portrait, portrait.get_rect(center=center))
            return

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
        elif enemy_type is EnemyType.GOBLIN:
            pygame.draw.circle(
                self.screen, GOBLIN_ENEMY_OUTLINE_COLOR, center, radius + 4
            )
            pygame.draw.circle(
                self.screen, GOBLIN_ENEMY_COLOR, center, radius
            )
            core_color = GOBLIN_ENEMY_CORE_COLOR
        elif enemy_type is EnemyType.NECROMANCER:
            points = (
                (center_x, center_y - radius - 4),
                (center_x + radius + 4, center_y),
                (center_x, center_y + radius + 4),
                (center_x - radius - 4, center_y),
            )
            pygame.draw.polygon(self.screen, NECROMANCER_ENEMY_OUTLINE_COLOR, points)
            pygame.draw.circle(
                self.screen, NECROMANCER_ENEMY_COLOR, center, radius
            )
            core_color = NECROMANCER_ENEMY_CORE_COLOR
        elif enemy_type is EnemyType.SKELETON:
            pygame.draw.circle(
                self.screen, SKELETON_ENEMY_OUTLINE_COLOR, center, radius + 4
            )
            pygame.draw.circle(
                self.screen, SKELETON_ENEMY_COLOR, center, radius
            )
            core_color = SKELETON_ENEMY_CORE_COLOR
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
                BOSS_ENEMY_COLOR if enemy_type is EnemyType.BOSS
                else ARMORED_ENEMY_OUTLINE_COLOR,
                outline_points,
            )
            pygame.draw.polygon(
                self.screen,
                BOSS_ENEMY_COLOR if enemy_type is EnemyType.BOSS
                else ARMORED_ENEMY_COLOR,
                body_points,
            )
            core_color = (
                BOSS_ENEMY_COLOR if enemy_type is EnemyType.BOSS
                else ARMORED_ENEMY_CORE_COLOR
            )

        pygame.draw.circle(self.screen, core_color, center, radius // 3)

    @staticmethod
    def _get_enemy_guide_color(enemy_type: EnemyType) -> tuple[int, int, int]:
        """Devuelve el color identificativo utilizado en la guía."""

        return {
            EnemyType.NORMAL: ENEMY_COLOR,
            EnemyType.FAST: FAST_ENEMY_COLOR,
            EnemyType.ARMORED: ARMORED_ENEMY_COLOR,
            EnemyType.GOBLIN: GOBLIN_ENEMY_COLOR,
            EnemyType.NECROMANCER: NECROMANCER_ENEMY_COLOR,
            EnemyType.SKELETON: SKELETON_ENEMY_COLOR,
            EnemyType.BOSS: BOSS_ENEMY_COLOR,
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
        enemy_types: list[EnemyType],
    ) -> str:
        """Construye el resumen de enemigos eliminados por tipo."""

        return "  |  ".join(
            (
                f"{enemy_type.plural_name}: "
                f"{defeated_enemies[enemy_type]}"
            )
            for enemy_type in enemy_types
        )
