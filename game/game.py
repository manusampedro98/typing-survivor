"""Controlador principal de Typing Survivor."""

from collections import Counter
from random import random

import pygame

from game.armored_enemy import ArmoredEnemy
from game.enemy import Enemy
from game.enemy_type import EnemyType
from game.fast_enemy import FastEnemy
from game.game_state import GameState
from game.settings import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    BATTLE_LANE_Y,
    BODY_FONT_SIZE,
    BORDER_COLOR,
    CARET_BLINK_INTERVAL,
    CARET_HEIGHT,
    CARET_WIDTH,
    CONTROL_INPUT_BLOCK_DURATION,
    CORRECT_COLOR,
    ENEMY_START_POSITION,
    FPS,
    GAME_OVER_OVERLAY_COLOR,
    INCORRECT_COLOR,
    INPUT_BOX_HEIGHT,
    INPUT_BOX_WIDTH,
    INPUT_HORIZONTAL_PADDING,
    KEY_REPEAT_DELAY,
    KEY_REPEAT_INTERVAL,
    MAX_COMBO_MULTIPLIER,
    MAX_INPUT_LENGTH,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
    PLAYER_COLOR,
    PLAYER_OUTLINE_COLOR,
    PLAYER_POSITION,
    PLAYER_RADIUS,
    POINTS_PER_CHARACTER,
    SMALL_FONT_SIZE,
    STARTING_LIVES,
    TARGET_FONT_SIZE,
    TEXT_COLOR,
    TITLE_FONT_SIZE,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WORDS_PER_WAVE,
    WORDS_PER_MULTIPLIER_LEVEL,
)
from game.typing_stats import TypingStats
from game.wave_manager import WaveManager
from game.word_manager import WordManager


class Game:
    """Controla la ventana, los eventos y el bucle principal del juego."""

    def __init__(self) -> None:
        """Inicializa Pygame y prepara los recursos principales."""

        # Inicializa los módulos internos necesarios para utilizar Pygame.
        pygame.init()

        # Crea la superficie principal sobre la que se dibuja la interfaz.
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)

        # El reloj controla la velocidad máxima del bucle principal.
        self.clock = pygame.time.Clock()
        self.running = True

        # Las fuentes se crean una sola vez para evitar hacerlo en cada fotograma.
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.target_font = pygame.font.Font(None, TARGET_FONT_SIZE)
        self.body_font = pygame.font.Font(None, BODY_FONT_SIZE)
        self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)

        # Carga la lista y selecciona la primera palabra objetivo.
        self.word_manager = WordManager()

        # Mantiene las métricas de escritura separadas de la lógica del juego.
        self.typing_stats = TypingStats()

        # Gestiona el aumento gradual de dificultad entre oleadas.
        self.wave_manager = WaveManager()

        # Registra el progreso básico de la sesión actual.
        self.completed_words = 0
        self.missed_words = 0
        self.lives = STARTING_LIVES
        self.score = 0
        self.combo = 0

        # Counter permite añadir nuevos tipos sin crear contadores separados.
        self.defeated_enemies: Counter[EnemyType] = Counter()
        self.state = GameState.MENU

        # Crea el primer enemigo asociado a la palabra seleccionada.
        self.enemy = self._create_enemy()

        # Almacena temporalmente los caracteres escritos por el jugador.
        self.typed_text = ""

        # Estado utilizado para hacer parpadear el cursor de escritura.
        self.caret_visible = True
        self.caret_last_toggle = pygame.time.get_ticks()

        # Marca hasta cuándo debe ignorarse una entrada usada como control.
        self.text_input_blocked_until = 0

        # Activa la recepción de texto respetando la distribución del teclado.
        pygame.key.start_text_input()

        # Permite mantener pulsadas teclas de control, como Retroceso.
        # Primero espera el retraso configurado y después repite a intervalos regulares.
        pygame.key.set_repeat(
            KEY_REPEAT_DELAY,
            KEY_REPEAT_INTERVAL,
        )

    def run(self) -> None:
        """Ejecuta el bucle principal hasta que el usuario cierre el juego."""

        try:
            while self.running:
                # Convierte los milisegundos del fotograma en segundos.
                delta_time = self.clock.tick(FPS) / 1000.0

                self._handle_events()
                self._update(delta_time)
                self._draw()
        finally:
            # Detiene la captura de texto y libera los recursos de Pygame.
            pygame.key.stop_text_input()
            pygame.quit()

    def _handle_events(self) -> None:
        """Procesa los eventos generados por el sistema y por el usuario."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self._handle_control_key(event)

            elif (
                event.type == pygame.TEXTINPUT
                and self.state is GameState.PLAYING
            ):
                current_time = pygame.time.get_ticks()

                if current_time >= self.text_input_blocked_until:
                    self._append_text(event.text)

    def _handle_control_key(self, event: pygame.event.Event) -> None:
        """Gestiona las teclas que controlan la aplicación o editan el texto."""

        # Escape tiene un comportamiento distinto según el estado actual.
        if event.key == pygame.K_ESCAPE:
            self._handle_escape_key()
            return

        if self.state is GameState.MENU:
            if event.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_SPACE,
            ):
                self._start_new_game()

        elif self.state is GameState.GAME_OVER:
            # Durante la derrota, R comienza una partida nueva.
            if event.key == pygame.K_r:
                self._start_new_game()

        elif (
            self.state is GameState.PLAYING
            and event.key == pygame.K_BACKSPACE
        ):
            # Evita modificar el texto si el campo ya está vacío.
            if self.typed_text:
                self.typed_text = self.typed_text[:-1]
                self._reset_caret_blink()

    def _handle_escape_key(self) -> None:
        """Pausa, reanuda o cierra según el estado actual."""

        if self.state is GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state is GameState.PAUSED:
            self.state = GameState.PLAYING
            self._block_text_input()
        else:
            # En el menú y al finalizar, Escape cierra la aplicación.
            self.running = False

    def _append_text(self, new_text: str) -> None:
        """Añade caracteres imprimibles sin superar el límite permitido."""

        if self.state is not GameState.PLAYING:
            return

        # Descarta posibles caracteres de control que no deben mostrarse.
        printable_text = "".join(
            character for character in new_text if character.isprintable()
        )

        # Impide escribir más caracteres de los que contiene la palabra objetivo.
        input_limit = min(
            MAX_INPUT_LENGTH,
            len(self.word_manager.current_word),
        )
        available_space = input_limit - len(self.typed_text)
        text_to_add = printable_text[:available_space]

        if text_to_add:
            start_index = len(self.typed_text)

            # Cada carácter aceptado cuenta como un intento para la precisión.
            for offset, character in enumerate(text_to_add):
                target_index = start_index + offset
                expected_character = self.word_manager.current_word[
                    target_index
                ]
                self.typing_stats.register_character(
                    character,
                    expected_character,
                )

            self.typed_text += text_to_add
            self._reset_caret_blink()

            if self.typed_text == self.word_manager.current_word:
                self._complete_current_word()

    def _complete_current_word(self) -> None:
        """Registra el acierto y prepara el siguiente objetivo."""

        # El combo se actualiza antes de calcular los puntos del acierto.
        self.combo += 1
        self.score += self._calculate_word_score(
            self.word_manager.current_word,
            self.enemy.score_multiplier,
        )
        self.completed_words += 1
        self.wave_manager.register_completed_word()
        self.word_manager.next_word()
        self.typed_text = ""

        if self.enemy.take_hit():
            self.defeated_enemies[self.enemy.enemy_type] += 1
            self.enemy = self._create_enemy()
        else:
            # El blindado conserva su posición y recibe un nuevo objetivo.
            self.enemy.word = self.word_manager.current_word

        self._reset_caret_blink()

    def _calculate_word_score(
        self,
        word: str,
        enemy_multiplier: int,
    ) -> int:
        """Calcula los puntos de una palabra según su longitud y combo."""

        base_score = len(word) * POINTS_PER_CHARACTER
        return (
            base_score
            * self._get_combo_multiplier()
            * enemy_multiplier
        )

    def _get_combo_multiplier(self) -> int:
        """Devuelve el multiplicador actual dentro del límite permitido."""

        multiplier = 1 + (self.combo - 1) // WORDS_PER_MULTIPLIER_LEVEL
        return min(multiplier, MAX_COMBO_MULTIPLIER)

    def _create_enemy(self) -> Enemy:
        """Crea un enemigo vinculado con la palabra objetivo actual."""

        # Una sola tirada distribuye probabilidades entre las variantes.
        enemy_roll = random()
        armored_limit = self.wave_manager.armored_enemy_chance
        fast_limit = armored_limit + self.wave_manager.fast_enemy_chance

        if enemy_roll < armored_limit:
            enemy_class = ArmoredEnemy
        elif enemy_roll < fast_limit:
            enemy_class = FastEnemy
        else:
            enemy_class = Enemy

        return enemy_class(
            word=self.word_manager.current_word,
            start_position=ENEMY_START_POSITION,
            target_position=PLAYER_POSITION,
            speed=self.wave_manager.enemy_speed,
        )

    def _update(self, delta_time: float) -> None:
        """Actualiza el cursor y el movimiento del enemigo."""

        # Solo la partida activa actualiza tiempo, cursor y movimiento.
        if self.state is not GameState.PLAYING:
            return

        current_time = pygame.time.get_ticks()

        # La medición se detiene automáticamente al finalizar la partida.
        self.typing_stats.update(delta_time)

        # Alterna la visibilidad del cursor cada cierto número de milisegundos.
        if current_time - self.caret_last_toggle >= CARET_BLINK_INTERVAL:
            self.caret_visible = not self.caret_visible
            self.caret_last_toggle = current_time

        self.enemy.update(delta_time)

        if self.enemy.has_reached_target():
            self._handle_enemy_arrival()

    def _handle_enemy_arrival(self) -> None:
        """Registra el fallo y prepara un enemigo con una palabra nueva."""

        self.missed_words += 1
        self.lives -= 1
        self.combo = 0
        self.typed_text = ""

        if self.lives <= 0:
            self.state = GameState.GAME_OVER
            return

        self.word_manager.next_word()
        self.enemy = self._create_enemy()
        self._reset_caret_blink()

    def _start_new_game(self) -> None:
        """Restablece el progreso y comienza una partida nueva."""

        self.completed_words = 0
        self.missed_words = 0
        self.lives = STARTING_LIVES
        self.score = 0
        self.combo = 0
        self.defeated_enemies.clear()
        self.state = GameState.PLAYING
        self.typed_text = ""
        self.typing_stats.reset()
        self.wave_manager.reset()

        self.word_manager.next_word()
        self.enemy = self._create_enemy()
        self._reset_caret_blink()
        self._block_text_input()

    def _block_text_input(self) -> None:
        """Impide que una tecla de control se añada al texto del jugador."""

        self.text_input_blocked_until = (
            pygame.time.get_ticks()
            + CONTROL_INPUT_BLOCK_DURATION
        )


    def _reset_caret_blink(self) -> None:
        """Muestra el cursor inmediatamente después de editar el texto."""

        self.caret_visible = True
        self.caret_last_toggle = pygame.time.get_ticks()

    def _draw(self) -> None:
        """Dibuja el fotograma actual y lo presenta en la ventana."""

        # Limpia el contenido del fotograma anterior.
        self.screen.fill(BACKGROUND_COLOR)

        self._draw_battlefield()
        self._draw_interface()

        if self.state is GameState.MENU:
            self._draw_menu()
        elif self.state is GameState.PAUSED:
            self._draw_pause()
        elif self.state is GameState.GAME_OVER:
            self._draw_game_over()

        # Muestra en pantalla todo lo dibujado durante este fotograma.
        pygame.display.flip()

    def _draw_interface(self) -> None:
        """Dibuja el título, las instrucciones y la zona de escritura."""

        title_surface = self.title_font.render(
            "TYPING SURVIVOR",
            True,
            ACCENT_COLOR,
        )
        title_rect = title_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 6)
        )
        self.screen.blit(title_surface, title_rect)

        subtitle_surface = self.small_font.render(
            "Entrena tu velocidad. Sobrevive escribiendo.",
            True,
            MUTED_TEXT_COLOR,
        )
        subtitle_rect = subtitle_surface.get_rect(
            center=(WINDOW_WIDTH // 2, title_rect.bottom + 30)
        )
        self.screen.blit(subtitle_surface, subtitle_rect)

        # Muestra la palabra que el jugador debe escribir.
        self._draw_target_word()
        self._draw_progress()
        self._draw_wave_progress()

        # El rectángulo del panel se centra automáticamente en la ventana.
        input_box = pygame.Rect(
            0,
            0,
            INPUT_BOX_WIDTH,
            INPUT_BOX_HEIGHT,
        )
        input_box.center = (
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 65,
        )

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

        # Define el punto fijo desde el que comienza el texto escrito.
        input_start_x = input_box.left + INPUT_HORIZONTAL_PADDING

        if self.typed_text:
            displayed_text = self.typed_text
            displayed_color = TEXT_COLOR
            text_x = input_start_x
        else:
            displayed_text = "Empieza a escribir..."
            displayed_color = MUTED_TEXT_COLOR

            # Deja espacio para mostrar el cursor delante del texto de ayuda.
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

        # Sitúa el cursor después del texto o al inicio cuando el campo está vacío.
        caret_x = text_rect.right + 3 if self.typed_text else input_start_x

        if self.caret_visible:
            caret_rect = pygame.Rect(
                caret_x,
                0,
                CARET_WIDTH,
                CARET_HEIGHT,
            )
            caret_rect.centery = input_box.centery

            pygame.draw.rect(
                self.screen,
                ACCENT_COLOR,
                caret_rect,
                border_radius=2,
            )

        help_surface = self.small_font.render(
            "Retroceso: borrar  |  Esc: pausa",
            True,
            MUTED_TEXT_COLOR,
        )
        help_rect = help_surface.get_rect(
            center=(WINDOW_WIDTH // 2, input_box.bottom + 45)
        )
        self.screen.blit(help_surface, help_rect)

    def _draw_target_word(self) -> None:
        """Dibuja la palabra objetivo y compara cada carácter escrito."""

        enemy_details = (
            f"{self.enemy.enemy_type.display_name}"
            f"  ·  x{self.enemy.score_multiplier} puntos"
        )

        if self.enemy.max_health > 1:
            enemy_details += (
                f"  ·  Escudo {self.enemy.health}/{self.enemy.max_health}"
            )

        type_surface = self.small_font.render(
            enemy_details,
            True,
            self.enemy.label_color,
        )
        type_rect = type_surface.get_rect(
            center=(
                round(self.enemy.position.x),
                round(self.enemy.position.y) - 98,
            )
        )
        self.screen.blit(type_surface, type_rect)

        character_surfaces = []

        # Asigna un color a cada carácter según el progreso del jugador.
        for index, character in enumerate(self.enemy.word):
            if index < len(self.typed_text):
                character_color = (
                    CORRECT_COLOR
                    if self.typed_text[index] == character
                    else INCORRECT_COLOR
                )
            else:
                character_color = TEXT_COLOR

            character_surface = self.target_font.render(
                character,
                True,
                character_color,
            )
            character_surfaces.append(character_surface)

        # Calcula el ancho total para centrar la palabra completa.
        total_width = sum(
            surface.get_width()
            for surface in character_surfaces
        )

        # Mantiene la palabra completa dentro de los límites de la ventana.
        half_word_width = total_width // 2
        word_center_x = max(
            half_word_width + 20,
            min(
                round(self.enemy.position.x),
                WINDOW_WIDTH - half_word_width - 20,
            ),
        )
        character_x = word_center_x - half_word_width
        word_center_y = round(self.enemy.position.y) - 58

        # Dibuja las letras una junto a otra conservando sus colores.
        for character_surface in character_surfaces:
            character_rect = character_surface.get_rect(
                midleft=(character_x, word_center_y)
            )
            self.screen.blit(character_surface, character_rect)
            character_x += character_surface.get_width()

    def _draw_battlefield(self) -> None:
        """Dibuja la trayectoria, el enemigo y la base provisional."""

        lane_start = (round(ENEMY_START_POSITION[0]), BATTLE_LANE_Y)
        lane_end = (round(PLAYER_POSITION[0]), BATTLE_LANE_Y)

        # La línea permite leer con claridad la trayectoria del enemigo.
        pygame.draw.line(
            self.screen,
            BORDER_COLOR,
            lane_start,
            lane_end,
            width=3,
        )

        self.enemy.draw(self.screen)

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

    def _draw_progress(self) -> None:
        """Muestra la puntuación y el progreso de la sesión."""

        # Sin combo activo, la interfaz muestra el multiplicador inicial.
        combo_multiplier = (
            self._get_combo_multiplier()
            if self.combo > 0
            else 1
        )

        progress_surface = self.small_font.render(
            (
                f"Puntos: {self.score}"
                f"  |  Combo: {self.combo} (x{combo_multiplier})"
                f"  |  Vidas: {self.lives}"
            ),
            True,
            MUTED_TEXT_COLOR,
        )
        progress_rect = progress_surface.get_rect(
            topright=(WINDOW_WIDTH - 30, 30)
        )
        self.screen.blit(progress_surface, progress_rect)

        typing_surface = self.small_font.render(
            (
                f"PPM: {self.typing_stats.words_per_minute:.1f}"
                f"  |  Precisión: {self.typing_stats.accuracy:.1f}%"
                f"  |  Errores: {self.typing_stats.errors}"
            ),
            True,
            MUTED_TEXT_COLOR,
        )
        typing_rect = typing_surface.get_rect(
            topright=(WINDOW_WIDTH - 30, progress_rect.bottom + 8)
        )
        self.screen.blit(typing_surface, typing_rect)

    def _draw_wave_progress(self) -> None:
        """Muestra la oleada y el avance hacia la siguiente."""

        wave_surface = self.body_font.render(
            f"OLEADA {self.wave_manager.current_wave}",
            True,
            ACCENT_COLOR,
        )
        wave_rect = wave_surface.get_rect(topleft=(30, 25))
        self.screen.blit(wave_surface, wave_rect)

        progress_surface = self.small_font.render(
            (
                f"Progreso: {self.wave_manager.completed_words_in_wave}"
                f"/{WORDS_PER_WAVE}"
            ),
            True,
            MUTED_TEXT_COLOR,
        )
        progress_rect = progress_surface.get_rect(
            topleft=(30, wave_rect.bottom + 5)
        )
        self.screen.blit(progress_surface, progress_rect)

        defeated_surface = self.small_font.render(
            self._get_enemy_defeat_summary(),
            True,
            MUTED_TEXT_COLOR,
        )
        defeated_rect = defeated_surface.get_rect(
            topleft=(30, progress_rect.bottom + 5)
        )
        self.screen.blit(defeated_surface, defeated_rect)

    def _get_enemy_defeat_summary(self) -> str:
        """Construye el resumen de enemigos eliminados por tipo."""

        return "  |  ".join(
            (
                f"{enemy_type.plural_name}: "
                f"{self.defeated_enemies[enemy_type]}"
            )
            for enemy_type in EnemyType
        )

    def _draw_game_over(self) -> None:
        """Dibuja una capa de derrota con las opciones disponibles."""

        self._draw_overlay()

        game_over_surface = self.title_font.render(
            "FIN DE LA PARTIDA",
            True,
            INCORRECT_COLOR,
        )
        game_over_rect = game_over_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 55)
        )
        self.screen.blit(game_over_surface, game_over_rect)

        result_surface = self.body_font.render(
            (
                f"Puntuación: {self.score}"
                f"  |  Palabras: {self.completed_words}"
                f"  |  Oleada: {self.wave_manager.current_wave}"
            ),
            True,
            TEXT_COLOR,
        )
        result_rect = result_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
        )
        self.screen.blit(result_surface, result_rect)

        defeated_surface = self.small_font.render(
            f"Eliminados  |  {self._get_enemy_defeat_summary()}",
            True,
            MUTED_TEXT_COLOR,
        )
        defeated_rect = defeated_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
        )
        self.screen.blit(defeated_surface, defeated_rect)

        stats_surface = self.small_font.render(
            (
                f"PPM: {self.typing_stats.words_per_minute:.1f}"
                f"  |  Precisión: {self.typing_stats.accuracy:.1f}%"
                f"  |  Errores: {self.typing_stats.errors}"
            ),
            True,
            MUTED_TEXT_COLOR,
        )
        stats_rect = stats_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 85)
        )
        self.screen.blit(stats_surface, stats_rect)

        restart_surface = self.small_font.render(
            "Pulsa R para reiniciar  |  Esc para cerrar",
            True,
            MUTED_TEXT_COLOR,
        )
        restart_rect = restart_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 130)
        )
        self.screen.blit(restart_surface, restart_rect)

    def _draw_menu(self) -> None:
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

        start_surface = self.body_font.render(
            "Pulsa Enter o Espacio para comenzar",
            True,
            TEXT_COLOR,
        )
        start_rect = start_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        )
        self.screen.blit(start_surface, start_rect)

        exit_surface = self.small_font.render(
            "Esc: cerrar",
            True,
            MUTED_TEXT_COLOR,
        )
        exit_rect = exit_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70)
        )
        self.screen.blit(exit_surface, exit_rect)

    def _draw_pause(self) -> None:
        """Dibuja una capa de pausa sobre la partida congelada."""

        self._draw_overlay()

        pause_surface = self.title_font.render(
            "PAUSA",
            True,
            ACCENT_COLOR,
        )
        pause_rect = pause_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 25)
        )
        self.screen.blit(pause_surface, pause_rect)

        continue_surface = self.small_font.render(
            "Pulsa Esc para continuar  |  Cierra la ventana para salir",
            True,
            MUTED_TEXT_COLOR,
        )
        continue_rect = continue_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 35)
        )
        self.screen.blit(continue_surface, continue_rect)

    def _draw_overlay(self) -> None:
        """Oscurece la partida para destacar una pantalla superpuesta."""

        # La transparencia conserva el contexto visual de la partida.
        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA,
        )
        overlay.fill(GAME_OVER_OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))
