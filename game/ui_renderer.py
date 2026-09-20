"""Representación visual de la interfaz y las pantallas del juego."""

from collections import Counter
import math

import pygame

from game.enemy_type import EnemyType
from game.game_state import GameState
from game.save_manager import HighScore
from game.settings import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    BORDER_COLOR,
    CARET_HEIGHT,
    CARET_WIDTH,
    COMBO_BAR_CENTER_Y,
    COMBO_BAR_HEIGHT,
    COMBO_BAR_WIDTH,
    GAME_OVER_OVERLAY_COLOR,
    INCORRECT_COLOR,
    INPUT_BOX_CENTER_Y,
    INPUT_BOX_HEIGHT,
    INPUT_BOX_WIDTH,
    INPUT_HORIZONTAL_PADDING,
    HUD_PANEL_MARGIN,
    MAX_COMBO_MULTIPLIER,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
    POWER_UP_COLOR,
    POWER_UP_PANEL_HEIGHT,
    POWER_UP_PANEL_TOP,
    POWER_UP_PANEL_WIDTH,
    POWER_UP_SLOT_SIZE,
    SLOW_POWER_UP_DURATION,
    STATS_PANEL_HEIGHT,
    STATS_PANEL_TOP,
    STATS_PANEL_WIDTH,
    TEXT_COLOR,
    WAVE_PANEL_HEIGHT,
    WAVE_PANEL_TOP,
    WAVE_PANEL_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    WORDS_PER_WAVE,
)
from game.typing_stats import TypingStats
from game.wave_manager import WaveManager


class UIRenderer:
    """Dibuja el HUD, el campo de escritura y las capas de estado."""

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
        high_score: HighScore,
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

        self._draw_session_progress(
            score=score,
            high_score=high_score,
            combo=combo,
            combo_multiplier=combo_multiplier,
            combo_progress=combo_progress,
            lives=lives,
            typing_stats=typing_stats,
        )
        self._draw_wave_progress(wave_manager)
        self._draw_power_up_panel(
            slow_charge_available,
            slow_time_remaining,
        )
        self._draw_input_box(typed_text, caret_visible)

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
    ) -> None:
        """Dibuja la pantalla superpuesta que corresponde al estado actual."""

        if state is GameState.MENU:
            self._draw_menu(high_score)
        elif state is GameState.COUNTDOWN:
            self._draw_countdown(countdown_remaining)
        elif state is GameState.PAUSED:
            self._draw_pause(audio_volume, audio_muted)
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

    def _draw_input_box(
        self,
        typed_text: str,
        caret_visible: bool,
    ) -> None:
        """Muestra el texto introducido y el cursor parpadeante."""

        input_box = pygame.Rect(0, 0, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)
        input_box.center = (WINDOW_WIDTH // 2, INPUT_BOX_CENTER_Y)

        pygame.draw.rect(
            self.screen,
            PANEL_COLOR,
            input_box,
            border_radius=12,
        )
        pygame.draw.rect(
            self.screen,
            BORDER_COLOR,
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

    def _draw_session_progress(
        self,
        score: int,
        high_score: HighScore,
        combo: int,
        combo_multiplier: int,
        combo_progress: float,
        lives: int,
        typing_stats: TypingStats,
    ) -> None:
        """Muestra puntuación, combo, vidas y métricas de escritura."""

        stats_panel = pygame.Rect(
            HUD_PANEL_MARGIN,
            STATS_PANEL_TOP,
            STATS_PANEL_WIDTH,
            STATS_PANEL_HEIGHT,
        )
        self._draw_panel(stats_panel)

        title_surface = self.small_font.render(
            "ESTADÍSTICAS",
            True,
            TEXT_COLOR,
        )
        title_rect = title_surface.get_rect(
            center=(stats_panel.centerx, stats_panel.top + 22)
        )
        self.screen.blit(title_surface, title_rect)

        stat_lines = (
            f"Puntos: {score}",
            f"Récord: {high_score.score}",
            f"Combo: {combo} (x{combo_multiplier})",
            f"Vidas: {lives}",
            f"PPM: {typing_stats.words_per_minute:.1f}",
            f"Precisión: {typing_stats.accuracy:.1f}%",
            f"Errores: {typing_stats.errors}",
        )

        line_y = stats_panel.top + 43

        for line in stat_lines:
            line_surface = self.small_font.render(
                line,
                True,
                MUTED_TEXT_COLOR,
            )
            line_rect = line_surface.get_rect(
                topleft=(stats_panel.left + 14, line_y)
            )
            self.screen.blit(line_surface, line_rect)
            line_y += 20

        self._draw_combo_bar(
            combo_multiplier=combo_multiplier,
            combo_progress=combo_progress,
        )

    def _draw_combo_bar(
        self,
        combo_multiplier: int,
        combo_progress: float,
    ) -> None:
        """Representa el avance hacia el siguiente multiplicador."""

        maximum_reached = combo_multiplier >= MAX_COMBO_MULTIPLIER

        if maximum_reached:
            label = f"COMBO MÁXIMO  x{MAX_COMBO_MULTIPLIER}"
        else:
            label = f"COMBO x{combo_multiplier}  >  x{combo_multiplier + 1}"

        label_surface = self.small_font.render(
            label,
            True,
            ACCENT_COLOR if maximum_reached else MUTED_TEXT_COLOR,
        )
        # En el nivel máximo no existe otra meta que representar con una barra.
        if maximum_reached:
            label_rect = label_surface.get_rect(
                center=(WINDOW_WIDTH // 2, COMBO_BAR_CENTER_Y)
            )
            self.screen.blit(label_surface, label_rect)
            return

        bar_rect = pygame.Rect(
            0,
            0,
            COMBO_BAR_WIDTH,
            COMBO_BAR_HEIGHT,
        )
        bar_rect.right = (WINDOW_WIDTH + INPUT_BOX_WIDTH) // 2
        bar_rect.centery = COMBO_BAR_CENTER_Y

        label_rect = label_surface.get_rect(
            midright=(bar_rect.left - 14, COMBO_BAR_CENTER_Y)
        )
        self.screen.blit(label_surface, label_rect)

        pygame.draw.rect(
            self.screen,
            PANEL_COLOR,
            bar_rect,
            border_radius=6,
        )
        pygame.draw.rect(
            self.screen,
            BORDER_COLOR,
            bar_rect,
            width=2,
            border_radius=6,
        )

        # El relleno se limita para mantener el dibujo dentro del borde.
        normalized_progress = max(0.0, min(1.0, combo_progress))
        fill_width = round((COMBO_BAR_WIDTH - 4) * normalized_progress)

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
                border_radius=4,
            )

    def _draw_wave_progress(
        self,
        wave_manager: WaveManager,
    ) -> None:
        """Muestra la oleada y el avance hacia la siguiente."""

        wave_panel = pygame.Rect(
            0,
            WAVE_PANEL_TOP,
            WAVE_PANEL_WIDTH,
            WAVE_PANEL_HEIGHT,
        )
        wave_panel.centerx = WINDOW_WIDTH // 2
        self._draw_panel(wave_panel)

        wave_surface = self.body_font.render(
            f"OLEADA {wave_manager.current_wave}",
            True,
            ACCENT_COLOR,
        )
        wave_rect = wave_surface.get_rect(
            center=(wave_panel.centerx, wave_panel.top + 24)
        )
        self.screen.blit(wave_surface, wave_rect)

        progress_surface = self.small_font.render(
            (
                f"Progreso: {wave_manager.completed_words_in_wave}"
                f"/{WORDS_PER_WAVE}"
            ),
            True,
            MUTED_TEXT_COLOR,
        )
        progress_rect = progress_surface.get_rect(
            center=(wave_panel.centerx, wave_panel.top + 55)
        )
        self.screen.blit(progress_surface, progress_rect)

    def _draw_power_up_panel(
        self,
        slow_charge_available: bool,
        slow_time_remaining: float,
    ) -> None:
        """Dibuja las ranuras reservadas para power-ups presentes y futuros."""

        power_up_panel = pygame.Rect(
            WINDOW_WIDTH - HUD_PANEL_MARGIN - POWER_UP_PANEL_WIDTH,
            POWER_UP_PANEL_TOP,
            POWER_UP_PANEL_WIDTH,
            POWER_UP_PANEL_HEIGHT,
        )
        self._draw_panel(power_up_panel)

        title_surface = self.small_font.render(
            "POTENCIADORES",
            True,
            TEXT_COLOR,
        )
        title_rect = title_surface.get_rect(
            center=(power_up_panel.centerx, power_up_panel.top + 22)
        )
        self.screen.blit(title_surface, title_rect)

        slot_gap = 12
        slots_width = POWER_UP_SLOT_SIZE * 3 + slot_gap * 2
        first_slot_left = power_up_panel.centerx - slots_width // 2
        slot_top = power_up_panel.top + 43

        for slot_index in range(6):
            slot_column = slot_index % 3
            slot_row = slot_index // 3
            slot_rect = pygame.Rect(
                first_slot_left
                + slot_column * (POWER_UP_SLOT_SIZE + slot_gap),
                slot_top
                + slot_row * (POWER_UP_SLOT_SIZE + slot_gap),
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
                border_radius=10,
            )
            pygame.draw.rect(
                self.screen,
                slot_color,
                slot_rect,
                width=2,
                border_radius=10,
            )

            key_surface = self.small_font.render(
                str(slot_index + 1),
                True,
                slot_color,
            )
            key_rect = key_surface.get_rect(
                topleft=(slot_rect.left + 7, slot_rect.top + 4)
            )
            self.screen.blit(key_surface, key_rect)

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
            "Pulsa R para reiniciar  |  Esc para cerrar",
            True,
            MUTED_TEXT_COLOR,
        )
        restart_rect = restart_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 155)
        )
        self.screen.blit(restart_surface, restart_rect)

    def _draw_menu(self, high_score: HighScore) -> None:
        """Dibuja el menú que espera antes de comenzar la partida."""

        self._draw_overlay()

        menu_title = self.title_font.render(
            "TYPING SURVIVOR",
            True,
            ACCENT_COLOR,
        )
        menu_title_rect = menu_title.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 55)
        )
        self.screen.blit(menu_title, menu_title_rect)

        record_surface = self.small_font.render(
            (
                f"Récord: {high_score.score} puntos"
                f"  |  Oleada {high_score.wave}"
                f"  |  {high_score.words_per_minute:.1f} PPM"
                f"  |  {high_score.accuracy:.1f}% precisión"
            ),
            True,
            MUTED_TEXT_COLOR,
        )
        record_rect = record_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 5)
        )
        self.screen.blit(record_surface, record_rect)

        start_surface = self.body_font.render(
            "Pulsa Enter o Espacio para comenzar",
            True,
            TEXT_COLOR,
        )
        start_rect = start_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 55)
        )
        self.screen.blit(start_surface, start_rect)

        exit_surface = self.small_font.render(
            "Esc: cerrar",
            True,
            MUTED_TEXT_COLOR,
        )
        exit_rect = exit_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100)
        )
        self.screen.blit(exit_surface, exit_rect)

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

        continue_surface = self.small_font.render(
            "Esc: continuar",
            True,
            MUTED_TEXT_COLOR,
        )
        continue_rect = continue_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 105)
        )
        self.screen.blit(continue_surface, continue_rect)

    def _draw_countdown(self, countdown_remaining: float) -> None:
        """Muestra el tiempo de preparación antes de activar la partida."""

        self._draw_overlay()

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

    def _draw_overlay(self) -> None:
        """Oscurece la partida para destacar una pantalla superpuesta."""

        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA,
        )
        overlay.fill(GAME_OVER_OVERLAY_COLOR)
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
