"""Controlador principal de Typing Survivor."""

from collections import Counter

import pygame

from game.battlefield_renderer import BattlefieldRenderer
from game.enemy import Enemy
from game.enemy_manager import EnemyManager
from game.enemy_type import EnemyType
from game.effects import EffectManager
from game.game_state import GameState
from game.save_manager import SaveManager
from game.settings import (
    BACKGROUND_COLOR,
    BODY_FONT_SIZE,
    CARET_BLINK_INTERVAL,
    CONTROL_INPUT_BLOCK_DURATION,
    COUNTDOWN_DURATION,
    FPS,
    KEY_REPEAT_DELAY,
    KEY_REPEAT_INTERVAL,
    MAX_COMBO_MULTIPLIER,
    MAX_INPUT_LENGTH,
    PLAYER_POSITION,
    POINTS_PER_CHARACTER,
    SMALL_FONT_SIZE,
    STARTING_LIVES,
    TARGET_FONT_SIZE,
    TITLE_FONT_SIZE,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WORDS_PER_MULTIPLIER_LEVEL,
)
from game.typing_stats import TypingStats
from game.ui_renderer import UIRenderer
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

        # El renderizador concentra toda la presentación de la arena.
        self.battlefield_renderer = BattlefieldRenderer(
            screen=self.screen,
            target_font=self.target_font,
            body_font=self.body_font,
            small_font=self.small_font,
        )

        # La interfaz tiene su propio renderizador y no altera la partida.
        self.ui_renderer = UIRenderer(
            screen=self.screen,
            title_font=self.title_font,
            body_font=self.body_font,
            small_font=self.small_font,
        )

        # Carga la lista y selecciona la primera palabra objetivo.
        self.word_manager = WordManager()

        # Mantiene las métricas de escritura separadas de la lógica del juego.
        self.typing_stats = TypingStats()

        # Gestiona el aumento gradual de dificultad entre oleadas.
        self.wave_manager = WaveManager()

        # Centraliza la creación y el movimiento de varios enemigos.
        self.enemy_manager = EnemyManager(
            self.word_manager,
            self.wave_manager,
        )

        # Gestiona partículas y mensajes sin mezclarlos con las entidades.
        self.effect_manager = EffectManager()

        # Carga el récord guardado fuera del repositorio del proyecto.
        self.save_manager = SaveManager()
        self.is_new_high_score = False

        # Registra el progreso básico de la sesión actual.
        self.completed_words = 0
        self.missed_words = 0
        self.lives = STARTING_LIVES
        self.score = 0
        self.combo = 0

        # Counter permite añadir nuevos tipos sin crear contadores separados.
        self.defeated_enemies: Counter[EnemyType] = Counter()
        self.state = GameState.MENU

        # La cuenta atrás conserva su propio tiempo sin mover enemigos.
        self.countdown_remaining = 0.0

        # Crea un enemigo inmóvil como fondo del menú inicial.
        self.enemy_manager.reset()

        # El objetivo se fija al escribir la primera letra de su palabra.
        self.active_enemy: Enemy | None = None

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

                # Vaciar el campo permite seleccionar otro enemigo.
                if not self.typed_text:
                    self.active_enemy = None

                self._reset_caret_blink()

    def _handle_escape_key(self) -> None:
        """Pausa, reanuda o cierra según el estado actual."""

        if self.state in (GameState.PLAYING, GameState.COUNTDOWN):
            self.state = GameState.PAUSED
        elif self.state is GameState.PAUSED:
            self._start_countdown()
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

        # Procesar uno a uno permite completar y seleccionar otro objetivo
        # incluso si el sistema entrega varios caracteres en un mismo evento.
        for character in printable_text:
            self._append_character(character)

    def _append_character(self, character: str) -> None:
        """Añade un carácter al objetivo seleccionado por su letra inicial."""

        if self.active_enemy is None:
            self.active_enemy = self.enemy_manager.select_target(character)

            if self.active_enemy is None:
                # Una inicial sin objetivo sigue contando como error de escritura.
                self.typing_stats.register_character(character, "")
                self._reset_caret_blink()
                return

        target_word = self.active_enemy.word
        input_limit = min(MAX_INPUT_LENGTH, len(target_word))

        if len(self.typed_text) >= input_limit:
            return

        expected_character = target_word[len(self.typed_text)]
        self.typing_stats.register_character(
            character,
            expected_character,
        )
        self.typed_text += character
        self._reset_caret_blink()

        if self.typed_text == target_word:
            self._complete_current_word()

    def _complete_current_word(self) -> None:
        """Registra el acierto y prepara el siguiente objetivo."""

        if self.active_enemy is None:
            return

        completed_enemy = self.active_enemy
        completed_word = completed_enemy.word

        # El combo se actualiza antes de calcular los puntos del acierto.
        self.combo += 1
        awarded_points = self._calculate_word_score(
            completed_word,
            completed_enemy.score_multiplier,
        )
        self.score += awarded_points
        self.completed_words += 1
        self.wave_manager.register_completed_word()
        self.typed_text = ""
        self.active_enemy = None

        enemy_defeated = completed_enemy.take_hit()
        self.effect_manager.create_enemy_feedback(
            position=completed_enemy.position,
            color=completed_enemy.label_color,
            awarded_points=awarded_points,
            defeated=enemy_defeated,
        )

        if enemy_defeated:
            self.defeated_enemies[completed_enemy.enemy_type] += 1
            self.enemy_manager.remove(completed_enemy)
        else:
            # El blindado conserva su posición y recibe un nuevo objetivo.
            self.enemy_manager.replace_word(completed_enemy)

        self.enemy_manager.ensure_enemy()
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

    def _update(self, delta_time: float) -> None:
        """Actualiza el cursor, las apariciones y los enemigos."""

        if self.state is GameState.COUNTDOWN:
            self._update_countdown(delta_time)
            return

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

        self.enemy_manager.update(delta_time)
        self._handle_enemy_arrivals()
        self.effect_manager.update(delta_time)

    def _update_countdown(self, delta_time: float) -> None:
        """Reduce la espera y activa la partida al llegar a cero."""

        self.countdown_remaining = max(
            0.0,
            self.countdown_remaining - delta_time,
        )

        if self.countdown_remaining == 0.0:
            self.state = GameState.PLAYING
            self._reset_caret_blink()
            self._block_text_input()

    def _handle_enemy_arrivals(self) -> None:
        """Resta vidas por cada enemigo que alcanza la base."""

        reached_enemies = self.enemy_manager.reached_enemies()

        for enemy in reached_enemies:
            self.effect_manager.create_player_damage(PLAYER_POSITION)
            self.enemy_manager.remove(enemy)
            self.missed_words += 1
            self.lives -= 1
            self.combo = 0

            # Solo se descarta el texto si pertenecía al enemigo alcanzado.
            if enemy is self.active_enemy:
                self.active_enemy = None
                self.typed_text = ""
                self._reset_caret_blink()

            if self.lives <= 0:
                self.state = GameState.GAME_OVER
                self._finish_game()
                return

        if reached_enemies:
            self.enemy_manager.ensure_enemy()

    def _start_new_game(self) -> None:
        """Restablece el progreso y comienza una partida nueva."""

        self.completed_words = 0
        self.missed_words = 0
        self.lives = STARTING_LIVES
        self.score = 0
        self.combo = 0
        self.is_new_high_score = False
        self.defeated_enemies.clear()
        self.typed_text = ""
        self.active_enemy = None
        self.typing_stats.reset()
        self.wave_manager.reset()
        self.enemy_manager.reset()
        self.effect_manager.reset()
        self._start_countdown()

    def _start_countdown(self) -> None:
        """Inicia el tiempo de preparación con la acción congelada."""

        self.countdown_remaining = COUNTDOWN_DURATION
        self.state = GameState.COUNTDOWN
        self._reset_caret_blink()
        self._block_text_input()

    def _finish_game(self) -> None:
        """Compara el resultado final con el récord almacenado."""

        self.is_new_high_score = self.save_manager.update_high_score(
            score=self.score,
            wave=self.wave_manager.current_wave,
            words_per_minute=self.typing_stats.words_per_minute,
            accuracy=self.typing_stats.accuracy,
        )

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

        self.battlefield_renderer.draw(
            enemy_manager=self.enemy_manager,
            active_enemy=self.active_enemy,
            typed_text=self.typed_text,
            effect_manager=self.effect_manager,
        )
        combo_multiplier = (
            self._get_combo_multiplier() if self.combo > 0 else 1
        )
        self.ui_renderer.draw_interface(
            typed_text=self.typed_text,
            caret_visible=self.caret_visible,
            score=self.score,
            high_score=self.save_manager.high_score,
            combo=self.combo,
            combo_multiplier=combo_multiplier,
            lives=self.lives,
            typing_stats=self.typing_stats,
            wave_manager=self.wave_manager,
            defeated_enemies=self.defeated_enemies,
        )
        self.ui_renderer.draw_state_overlay(
            state=self.state,
            countdown_remaining=self.countdown_remaining,
            high_score=self.save_manager.high_score,
            is_new_high_score=self.is_new_high_score,
            score=self.score,
            completed_words=self.completed_words,
            wave_manager=self.wave_manager,
            defeated_enemies=self.defeated_enemies,
            typing_stats=self.typing_stats,
        )

        # Muestra en pantalla todo lo dibujado durante este fotograma.
        pygame.display.flip()
