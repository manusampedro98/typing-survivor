"""Controlador principal de Typing Survivor."""

from collections import Counter
import ctypes
from ctypes import wintypes
import math
from pathlib import Path
import sys
import webbrowser

import pygame

from game.armored_enemy import ArmoredEnemy
from game.audio_manager import AudioManager
from game.battlefield_renderer import BattlefieldRenderer
from game.difficulty import Difficulty
from game.enemy import Enemy
from game.enemy_manager import EnemyManager
from game.enemy_type import EnemyType
from game.effects import EffectManager
from game.game_state import GameState
from game.power_up_manager import PowerUpManager
from game.power_up_type import PowerUpType
from game.projectile_manager import EnergyHit, ProjectileManager
from game.save_manager import SaveManager
from game.talents import (
    ARMORED_KNOCKBACK_DISTANCE,
    DROP_BONUS_MULTIPLIER,
    SHIELD_REACTION_DISTANCE,
    SHIELD_REACTION_RADIUS,
    TALENTS,
)
from game.settings import (
    AUDIO_VOLUME_STEP,
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
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MULTISHOT_CHAIN_TARGETS,
    PLAYER_POSITION,
    POINTS_PER_CHARACTER,
    SMALL_FONT_SIZE,
    SKELETON_POWER_UP_CHANCE_MULTIPLIER,
    STARTING_LIVES,
    TARGET_FONT_SIZE,
    TITLE_FONT_SIZE,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WAVE_BREAK_DURATION,
    WORDS_PER_MULTIPLIER_LEVEL,
)
from game.typing_stats import TypingStats
from game.ui_renderer import UIRenderer
from game.wave_manager import WaveManager
from game.word_manager import WordManager


LINKEDIN_URL = "https://www.linkedin.com/in/manu-sampedro-196475409/"
GITHUB_URL = "https://github.com/manusampedro98?tab=repositories"
APP_ICON_FILE = (
    Path(__file__).resolve().parent.parent / "assets" / "images" / "ui" / "app_icon.png"
)


class Game:
    """Controla la ventana, los eventos y el bucle principal del juego."""

    def __init__(self) -> None:
        """Inicializa Pygame y prepara los recursos principales."""

        # Inicializa los módulos internos necesarios para utilizar Pygame.
        pygame.init()

        # Se establece antes de crear la ventana para que Windows use el icono.
        try:
            icon = pygame.image.load(str(APP_ICON_FILE))
            pygame.display.set_icon(pygame.transform.smoothscale(icon, (32, 32)))
        except (OSError, pygame.error):
            # Un problema con el icono no debe impedir iniciar la partida.
            pass

        # La ventana puede cambiar de tamaño sin alterar las coordenadas del juego.
        self.display_surface = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.RESIZABLE,
        )
        self.windowed_size = self.display_surface.get_size()
        self.windowed_position = self._get_window_position()
        self.is_fullscreen = False

        # Todo se dibuja primero sobre una superficie lógica de tamaño estable.
        self.screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
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

        # Gestiona las bolas de energía y comunica cuándo alcanzan su objetivo.
        self.projectile_manager = ProjectileManager()

        # Gestiona las cargas y los efectos temporales de los power-ups.
        self.power_up_manager = PowerUpManager()

        # Centraliza la música, los efectos y los controles de volumen.
        self.audio_manager = AudioManager()
        self.audio_manager.start_music()

        # Carga el récord guardado fuera del repositorio del proyecto.
        self.save_manager = SaveManager()
        self.is_new_high_score = False

        # Registra el progreso básico de la sesión actual.
        self.completed_words = 0
        self.missed_words = 0
        self.max_lives = STARTING_LIVES + self.save_manager.talent_level("extra_life")
        self.lives = self.max_lives
        self.bonus_heart_active = False
        self.last_breath_used = False
        self.word_had_error = False
        self.run_reward_banked = False
        self.score = 0
        self.combo = 0

        # Counter permite añadir nuevos tipos sin crear contadores separados.
        self.defeated_enemies: Counter[EnemyType] = Counter()
        self.state = GameState.MENU

        # La portada conserva el foco de teclado y la dificultad seleccionada.
        self.menu_selection = 0
        self.game_over_selection = 0
        self.shop_selection = 0
        self.shop_message = ""
        self.submenu_return_state = GameState.MENU
        self.difficulty_selection = 1
        self.selected_difficulty = Difficulty.NORMAL
        self.showing_revive = False
        self.dragging_volume_slider = False

        # La ayuda recuerda si debe regresar al menú, la pausa o el resultado.
        self.help_return_state = GameState.MENU
        self.help_page = "menu"
        self.help_selection = 0

        # La cuenta atrás conserva su propio tiempo sin mover enemigos.
        self.countdown_remaining = 0.0
        self.wave_break_remaining = 0.0

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

            elif event.type == pygame.VIDEORESIZE:
                self._resize_window(event.w, event.h)

            elif event.type == pygame.KEYDOWN:
                self._handle_control_key(event)

            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_click(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_volume_slider = False

            elif (
                event.type == pygame.TEXTINPUT
                and self.state is GameState.PLAYING
            ):
                current_time = pygame.time.get_ticks()

                if current_time >= self.text_input_blocked_until:
                    self._append_text(event.text)

    def _handle_control_key(self, event: pygame.event.Event) -> None:
        """Gestiona las teclas que controlan la aplicación o editan el texto."""

        # F11 mantiene el comportamiento habitual de las aplicaciones de escritorio.
        if event.key == pygame.K_F11:
            self._toggle_fullscreen()
            return

        # Escape tiene un comportamiento distinto según el estado actual.
        if event.key == pygame.K_ESCAPE:
            self._handle_escape_key()
            return

        if self.state is GameState.MENU:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu_selection = (
                    self.menu_selection - 1
                ) % len(self.ui_renderer.main_menu_actions)
                self.audio_manager.play("menu_adjust")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_selection = (
                    self.menu_selection + 1
                ) % len(self.ui_renderer.main_menu_actions)
                self.audio_manager.play("menu_adjust")
            if event.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_SPACE,
            ):
                self._activate_menu_action(
                    self.ui_renderer.main_menu_actions[self.menu_selection]
                )
            elif event.key == pygame.K_h:
                self._open_help()

        elif self.state is GameState.SHOP:
            previous_selection = self.shop_selection
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.shop_selection = (self.shop_selection - 1) % len(TALENTS)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.shop_selection = (self.shop_selection + 1) % len(TALENTS)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.shop_selection = (self.shop_selection - 2) % len(TALENTS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.shop_selection = (self.shop_selection + 2) % len(TALENTS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._buy_selected_talent()
            if self.shop_selection != previous_selection:
                self.shop_message = ""
                self.audio_manager.play("menu_adjust")

        elif self.state is GameState.DIFFICULTY:
            if event.key in (
                pygame.K_LEFT,
                pygame.K_UP,
                pygame.K_a,
                pygame.K_w,
            ):
                self.difficulty_selection = (
                    self.difficulty_selection - 1
                ) % len(Difficulty)
                self.audio_manager.play("menu_adjust")
            elif event.key in (
                pygame.K_RIGHT,
                pygame.K_DOWN,
                pygame.K_d,
                pygame.K_s,
            ):
                self.difficulty_selection = (
                    self.difficulty_selection + 1
                ) % len(Difficulty)
                self.audio_manager.play("menu_adjust")
            elif event.key in (
                pygame.K_RETURN,
                pygame.K_KP_ENTER,
                pygame.K_SPACE,
            ):
                self.selected_difficulty = list(Difficulty)[
                    self.difficulty_selection
                ]
                self._start_new_game(self.selected_difficulty)

        elif self.state is GameState.OPTIONS:
            if event.key in (pygame.K_LEFT, pygame.K_MINUS, pygame.K_KP_MINUS):
                self.audio_manager.change_volume(-AUDIO_VOLUME_STEP)
                self.audio_manager.play("menu_adjust")
            elif event.key in (
                pygame.K_RIGHT,
                pygame.K_PLUS,
                pygame.K_EQUALS,
                pygame.K_KP_PLUS,
            ):
                self.audio_manager.change_volume(AUDIO_VOLUME_STEP)
                self.audio_manager.play("menu_adjust")
            elif event.key == pygame.K_m:
                self.audio_manager.toggle_mute()
                if not self.audio_manager.muted:
                    self.audio_manager.play("menu_adjust")

        elif self.state is GameState.HELP and self.help_page == "menu":
            if event.key in (pygame.K_UP, pygame.K_w):
                self.help_selection = (
                    self.help_selection - 1
                ) % len(self.ui_renderer.help_section_actions)
                self.audio_manager.play("menu_adjust")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.help_selection = (
                    self.help_selection + 1
                ) % len(self.ui_renderer.help_section_actions)
                self.audio_manager.play("menu_adjust")
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._activate_help_action(
                    self.ui_renderer.help_section_actions[self.help_selection]
                )

        elif self.state is GameState.GAME_OVER:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.game_over_selection = (
                    self.game_over_selection - 1
                ) % len(self.ui_renderer.game_over_actions)
                self.audio_manager.play("menu_adjust")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.game_over_selection = (
                    self.game_over_selection + 1
                ) % len(self.ui_renderer.game_over_actions)
                self.audio_manager.play("menu_adjust")
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._activate_game_over_action(
                    self.ui_renderer.game_over_actions[self.game_over_selection]
                )
            elif event.key == pygame.K_r:
                self._activate_game_over_action("REINICIAR")
            elif event.key == pygame.K_h:
                self._activate_game_over_action("AYUDA")

        elif self.state is GameState.PAUSED:
            # El audio solo se modifica desde el menú de pausa.
            if event.key in (pygame.K_LEFT, pygame.K_MINUS, pygame.K_KP_MINUS):
                self.audio_manager.change_volume(-AUDIO_VOLUME_STEP)
                self.audio_manager.play("menu_adjust")
            elif event.key in (
                pygame.K_RIGHT,
                pygame.K_PLUS,
                pygame.K_EQUALS,
                pygame.K_KP_PLUS,
            ):
                self.audio_manager.change_volume(AUDIO_VOLUME_STEP)
                self.audio_manager.play("menu_adjust")
            elif event.key == pygame.K_m:
                self.audio_manager.toggle_mute()

                # Al recuperar el sonido ofrece una confirmación audible.
                if not self.audio_manager.muted:
                    self.audio_manager.play("menu_adjust")
            elif event.key == pygame.K_h:
                self._open_help()

        elif self.state is GameState.PLAYING:
            power_up_keys = {
                pygame.K_1: 0,
                pygame.K_KP1: 0,
                pygame.K_2: 1,
                pygame.K_KP2: 1,
                pygame.K_3: 2,
                pygame.K_KP3: 2,
                pygame.K_4: 3,
                pygame.K_KP4: 3,
            }

            if event.key in power_up_keys:
                self._activate_power_up_slot(power_up_keys[event.key])
                self._block_text_input()
            elif event.key == pygame.K_BACKSPACE:
                # Evita modificar el texto si el campo ya está vacío.
                if self.typed_text:
                    self.typed_text = self.typed_text[:-1]
                    self.audio_manager.play_backspace()

                    # Vaciar el campo permite seleccionar otro enemigo.
                    candidates = self.enemy_manager.matching_targets(
                        self.typed_text
                    ) if self.typed_text else []
                    self.active_enemy = (
                        candidates[0] if len(candidates) == 1 else None
                    )

                    self._reset_caret_blink()

    def _handle_escape_key(self) -> None:
        """Pausa, reanuda o cierra según el estado actual."""

        if self.state is GameState.HELP:
            if self.help_page == "menu":
                self.state = self.help_return_state
            else:
                self.help_page = "menu"
        elif self.state in (GameState.OPTIONS, GameState.SHOP):
            self.state = self.submenu_return_state
            self.dragging_volume_slider = False
        elif self.state in (
            GameState.DIFFICULTY,
            GameState.CREDITS,
            GameState.CONTACT,
        ):
            self.state = GameState.MENU
            self.dragging_volume_slider = False
        elif self.state in (GameState.DYING, GameState.WAVE_BREAK):
            # La breve secuencia final no se interrumpe con Escape.
            return
        elif self.state in (GameState.PLAYING, GameState.COUNTDOWN):
            self.state = GameState.PAUSED
        elif self.state is GameState.PAUSED:
            self._start_countdown()
        else:
            # En el menú y al finalizar, Escape cierra la aplicación.
            self.running = False

    def _open_help(self) -> None:
        """Abre la ayuda y conserva la pantalla desde la que se accedió."""

        self.help_return_state = self.state
        self.help_page = "menu"
        self.help_selection = 0
        self.state = GameState.HELP
        self.audio_manager.play("menu_adjust")

    def _activate_help_action(self, action: str) -> None:
        """Abre una ficha o regresa desde la ayuda."""

        if action == "CERRAR":
            self.state = self.help_return_state
        elif action == "VOLVER":
            self.help_page = "menu"
        elif action in self.ui_renderer.help_section_actions:
            self.help_page = "controls" if action == "CONTROLES" else "enemies"
        else:
            return
        self.audio_manager.play("menu_adjust")

    def _activate_menu_action(self, action: str) -> None:
        """Ejecuta la opción elegida en la pantalla de inicio."""

        if action == "JUGAR":
            self.state = GameState.DIFFICULTY
        elif action == "OPCIONES":
            self.submenu_return_state = GameState.MENU
            self.state = GameState.OPTIONS
        elif action == "TIENDA":
            self.submenu_return_state = GameState.MENU
            self.shop_selection = 0
            self.shop_message = ""
            self.state = GameState.SHOP
        elif action == "AYUDA":
            self._open_help()
        elif action == "CRÉDITOS":
            self.state = GameState.CREDITS
        elif action == "CONTACTO":
            self.state = GameState.CONTACT
        elif action == "SALIR":
            self.running = False

    def _activate_game_over_action(self, action: str) -> None:
        """Ejecuta la acción seleccionada tras terminar una partida."""

        if action == "REINICIAR":
            self._start_new_game()
        elif action == "TIENDA":
            self.submenu_return_state = GameState.GAME_OVER
            self.shop_selection = 0
            self.shop_message = ""
            self.state = GameState.SHOP
        elif action == "AYUDA":
            self._open_help()
        elif action == "OPCIONES":
            self.submenu_return_state = GameState.GAME_OVER
            self.state = GameState.OPTIONS
        elif action == "SALIR":
            self.running = False

    def _buy_selected_talent(self) -> None:
        """Compra el nivel seleccionado y comunica el resultado al jugador."""

        talent = TALENTS[self.shop_selection]
        level = self.save_manager.talent_level(talent.key)
        price = talent.next_cost(level)
        if price is None:
            self.shop_message = "NIVEL MÁXIMO"
        elif self.save_manager.available_points < price:
            self.shop_message = "PUNTOS INSUFICIENTES"
        elif self.save_manager.purchase_talent(talent.key):
            self.shop_message = f"{talent.name.upper()} COMPRADO"
            self.audio_manager.play("power_up_activate")
        else:
            self.shop_message = "NO SE PUDO GUARDAR LA COMPRA"

    def _handle_mouse_motion(self, position: tuple[int, int]) -> None:
        """Traslada el foco del menú al botón situado bajo el puntero."""

        logical_position = self._display_to_logical(position)
        if logical_position is None:
            return

        if self.state is GameState.MENU:
            action = self.ui_renderer.get_menu_action_at(logical_position)
            if action in self.ui_renderer.main_menu_actions:
                self.menu_selection = self.ui_renderer.main_menu_actions.index(
                    action
                )
        elif self.state is GameState.GAME_OVER:
            action = self.ui_renderer.get_game_over_action_at(logical_position)
            if action in self.ui_renderer.game_over_actions:
                self.game_over_selection = self.ui_renderer.game_over_actions.index(
                    action
                )
        elif self.state is GameState.DIFFICULTY:
            difficulty_index = self.ui_renderer.get_difficulty_at(
                logical_position
            )
            if difficulty_index is not None:
                self.difficulty_selection = difficulty_index
        elif self.state is GameState.SHOP:
            action = self.ui_renderer.get_shop_action_at(logical_position)
            if isinstance(action, int) and action != self.shop_selection:
                self.shop_selection = action
                self.shop_message = ""
        elif self.state in (GameState.OPTIONS, GameState.PAUSED) and self.dragging_volume_slider:
            self._set_volume_from_slider(logical_position)
        elif self.state is GameState.HELP and self.help_page == "menu":
            action = self.ui_renderer.get_help_action_at(
                logical_position, self.help_page
            )
            if action in self.ui_renderer.help_section_actions:
                self.help_selection = self.ui_renderer.help_section_actions.index(
                    action
                )

    def _handle_mouse_click(self, position: tuple[int, int]) -> None:
        """Activa botones de portada y tarjetas de dificultad con el ratón."""

        logical_position = self._display_to_logical(position)
        if logical_position is None:
            return

        if self.state is GameState.MENU:
            action = self.ui_renderer.get_menu_action_at(logical_position)
            if action is not None:
                self.audio_manager.play("menu_adjust")
                self._activate_menu_action(action)
        elif self.state is GameState.GAME_OVER:
            action = self.ui_renderer.get_game_over_action_at(logical_position)
            if action is not None:
                self.game_over_selection = self.ui_renderer.game_over_actions.index(
                    action
                )
                self.audio_manager.play("menu_adjust")
                self._activate_game_over_action(action)
        elif self.state is GameState.DIFFICULTY:
            difficulty_index = self.ui_renderer.get_difficulty_at(
                logical_position
            )
            if difficulty_index is not None:
                self.difficulty_selection = difficulty_index
                self.selected_difficulty = list(Difficulty)[difficulty_index]
                self._start_new_game(self.selected_difficulty)
        elif self.state is GameState.SHOP:
            action = self.ui_renderer.get_shop_action_at(logical_position)
            if action == "CERRAR":
                self.state = self.submenu_return_state
            elif isinstance(action, int):
                self.shop_selection = action
                self._buy_selected_talent()
        elif self.state is GameState.OPTIONS:
            action = self.ui_renderer.get_options_control_at(logical_position)
            if action == "CERRAR":
                self.state = self.submenu_return_state
            elif action == "VOLUMEN":
                self.dragging_volume_slider = True
                self._set_volume_from_slider(logical_position)
            elif action == "MUTE":
                self.audio_manager.toggle_mute()
                if not self.audio_manager.muted:
                    self.audio_manager.play("menu_adjust")
            elif action == "PANTALLA_COMPLETA":
                self._toggle_fullscreen()
        elif self.state is GameState.PAUSED:
            action = self.ui_renderer.get_pause_control_at(logical_position)
            if action == "VOLUMEN":
                self.dragging_volume_slider = True
                self._set_volume_from_slider(logical_position)
            elif action == "MUTE":
                self.audio_manager.toggle_mute()
                if not self.audio_manager.muted:
                    self.audio_manager.play("menu_adjust")
            elif action == "AYUDA":
                self._open_help()
            elif action == "CONTINUAR":
                self._start_countdown()
        elif self.state is GameState.HELP:
            action = self.ui_renderer.get_help_action_at(
                logical_position, self.help_page
            )
            if action is not None:
                self._activate_help_action(action)
        elif self.state in (GameState.CREDITS, GameState.CONTACT):
            action = self.ui_renderer.get_information_action_at(
                logical_position
            )
            if action == "CERRAR":
                self.state = GameState.MENU
            elif action == "LINKEDIN":
                webbrowser.open(LINKEDIN_URL, new=2)
            elif action == "GITHUB":
                webbrowser.open(GITHUB_URL, new=2)

    def _set_volume_from_slider(self, position: tuple[int, int]) -> None:
        """Actualiza el volumen según la posición pulsada en el deslizador."""

        if self.state is GameState.PAUSED:
            volume = self.ui_renderer.get_pause_volume_from_position(position)
        else:
            volume = self.ui_renderer.get_volume_from_position(position)
        self.audio_manager.set_volume(volume)

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
        """Mantiene abiertos los objetivos que comparten prefijo."""

        self.battlefield_renderer.register_player_keystroke()
        self.audio_manager.play_typing_key()

        if self.active_enemy is None:
            proposed_text = self.typed_text + character
            candidates = self.enemy_manager.matching_targets(proposed_text)
            if candidates:
                self.typing_stats.register_character(character, character)
                self.typed_text = proposed_text
                # Una palabra exacta se resuelve aunque otra sea más larga.
                exact_match = next(
                    (enemy for enemy in candidates if enemy.word == proposed_text),
                    None,
                )
                if exact_match is not None:
                    self.active_enemy = exact_match
                elif len(candidates) == 1:
                    self.active_enemy = candidates[0]
                self._reset_caret_blink()
                if self.active_enemy is not None and (
                    self.typed_text == self.active_enemy.word
                ):
                    self._complete_current_word()
                return

            if not self.typed_text:
                # Una inicial sin objetivo no inicia la escritura.
                self._reset_caret_blink()
                return

            # Un error en un prefijo ambiguo se asigna al candidato más
            # cercano, de modo que Retroceso pueda corregirlo.
            self.active_enemy = self.enemy_manager.select_target(
                self.typed_text
            )
            if self.active_enemy is None:
                self.typed_text = ""
                self._reset_caret_blink()
                return

        target_word = self.active_enemy.word
        input_limit = (
            len(target_word)
            if self.active_enemy.enemy_type is EnemyType.BOSS
            else min(MAX_INPUT_LENGTH, len(target_word))
        )

        if len(self.typed_text) >= input_limit:
            return

        expected_character = target_word[len(self.typed_text)]
        self.typing_stats.register_character(
            character,
            expected_character,
        )
        if character != expected_character:
            self.word_had_error = True
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
        if not self.word_had_error:
            self.power_up_manager.trigger_precision_slow(
                self.save_manager.talent_level("precision_pulse")
            )
        self.word_had_error = False
        self.typed_text = ""
        self.active_enemy = None

        # El daño sigue esperando a la bola. El blindado expone de inmediato
        # su segunda palabra y permite escribirla durante ese trayecto.
        completed_enemy.pending_hits += 1
        completed_enemy.is_pending_hit = True
        if (
            isinstance(completed_enemy, ArmoredEnemy)
            and completed_enemy.enemy_type is EnemyType.ARMORED
            and completed_enemy.second_word is not None
        ):
            self.enemy_manager.replace_word(completed_enemy)
            completed_enemy.is_pending_hit = False
        chain_targets: list[Enemy] = []
        if self.power_up_manager.multishot_armed:
            chain_targets = self.enemy_manager.get_chain_targets(
                excluded_enemy=completed_enemy,
                limit=(
                    MULTISHOT_CHAIN_TARGETS
                    + self.save_manager.talent_level("multishot_plus")
                ),
            )

        if chain_targets and self.power_up_manager.consume_multishot():
            for chain_target in chain_targets:
                chain_target.pending_hits += 1
                chain_target.is_pending_hit = True
            self.projectile_manager.launch_chain(
                completed_enemy,
                chain_targets,
                awarded_points,
            )
        else:
            self.projectile_manager.launch(completed_enemy, awarded_points)

        # Si era el último objetivo disponible, se crea otro mientras el
        # proyectil completa su recorrido para mantener el ritmo de escritura.
        self.enemy_manager.ensure_enemy()
        self._reset_caret_blink()

    def _resolve_energy_hits(self, energy_hits: list[EnergyHit]) -> None:
        """Aplica el daño cuando cada proyectil alcanza realmente al enemigo."""

        wave_completed = False
        defeated_boss = False
        for energy_hit in energy_hits:
            enemy = energy_hit.enemy

            # Un reinicio puede retirar objetivos con proyectiles pendientes.
            if enemy not in self.enemy_manager.enemies:
                continue

            enemy.pending_hits = max(0, enemy.pending_hits - 1)
            enemy.is_pending_hit = enemy.pending_hits > 0
            enemy_defeated = enemy.take_hit()
            self.effect_manager.create_enemy_feedback(
                position=energy_hit.position,
                color=enemy.label_color,
                awarded_points=energy_hit.awarded_points,
                defeated=enemy_defeated,
            )

            if enemy_defeated:
                self.audio_manager.play("enemy_defeat")
                self.defeated_enemies[enemy.enemy_type] += 1
                self.battlefield_renderer.play_enemy_death(enemy)
                if enemy.enemy_type is EnemyType.BOSS:
                    defeated_boss = True

                charge_multiplier = (
                    SKELETON_POWER_UP_CHANCE_MULTIPLIER
                    if enemy.enemy_type is EnemyType.SKELETON else 1.0
                )
                if self.save_manager.talent_level("more_drops"):
                    charge_multiplier *= DROP_BONUS_MULTIPLIER
                granted_power_up = self.power_up_manager.try_grant_charge(
                    charge_multiplier
                )
                if granted_power_up is not None:
                    self.effect_manager.create_power_up_drop(
                        energy_hit.position, granted_power_up
                    )
                    if granted_power_up.is_automatic:
                        self._activate_automatic_power_up(granted_power_up)
                    else:
                        self.audio_manager.play("power_up_ready")

                self.enemy_manager.remove(enemy)
                if self.wave_manager.register_defeat(
                    is_skeleton=enemy.enemy_type is EnemyType.SKELETON,
                    is_boss=enemy.enemy_type is EnemyType.BOSS,
                ):
                    wave_completed = True
            else:
                self.audio_manager.play("enemy_hit")
                self.battlefield_renderer.play_enemy_damage(enemy)
                if (
                    enemy.enemy_type is EnemyType.ARMORED
                    and enemy.health == enemy.max_health - 1
                    and self.save_manager.talent_level("armor_break")
                ):
                    self.enemy_manager.push_enemy_away(
                        enemy, PLAYER_POSITION, ARMORED_KNOCKBACK_DISTANCE
                    )
                # La segunda palabra del blindado ya se hizo visible al disparar.
                if not (
                    isinstance(enemy, ArmoredEnemy)
                    and enemy.enemy_type is EnemyType.ARMORED
                    and enemy.second_word_exposed
                ):
                    self.enemy_manager.replace_word(enemy)

        if wave_completed:
            self._begin_wave_break(preserve_boss_death=defeated_boss)
        elif energy_hits:
            self.enemy_manager.ensure_enemy()

    def _calculate_word_score(
        self,
        word: str,
        enemy_multiplier: float,
    ) -> int:
        """Calcula los puntos de una palabra según su longitud y combo."""

        base_score = len(word) * POINTS_PER_CHARACTER
        return round(
            base_score
            * self._get_combo_multiplier()
            * enemy_multiplier
            * self.power_up_manager.score_multiplier
        )

    def _get_combo_multiplier(self) -> int:
        """Devuelve el multiplicador actual dentro del límite permitido."""

        if self.combo <= 0:
            return 1

        multiplier = 1 + (self.combo - 1) // WORDS_PER_MULTIPLIER_LEVEL
        return min(multiplier, MAX_COMBO_MULTIPLIER)

    def _get_combo_progress(self) -> float:
        """Calcula el llenado hacia el siguiente multiplicador."""

        if self.combo <= 0:
            return 0.0

        if self._get_combo_multiplier() >= MAX_COMBO_MULTIPLIER:
            return 1.0

        words_in_level = (
            (self.combo - 1) % WORDS_PER_MULTIPLIER_LEVEL
        ) + 1
        return words_in_level / WORDS_PER_MULTIPLIER_LEVEL

    def _update(self, delta_time: float) -> None:
        """Actualiza el cursor, las apariciones y los enemigos."""

        # La animación idle se mantiene activa en las pantallas con movimiento
        # y se congela junto con la acción durante la pausa o el resultado.
        if self.state in (
            GameState.MENU,
            GameState.DIFFICULTY,
            GameState.OPTIONS,
            GameState.SHOP,
            GameState.CREDITS,
            GameState.CONTACT,
            GameState.COUNTDOWN,
            GameState.PLAYING,
            GameState.WAVE_BREAK,
            GameState.DYING,
        ):
            self.battlefield_renderer.update(delta_time)
            self.ui_renderer.update(delta_time)

        if self.state is GameState.COUNTDOWN:
            self._update_countdown(delta_time)
            self.effect_manager.update(delta_time)
            return

        if self.state is GameState.WAVE_BREAK:
            self._update_wave_break(delta_time)
            return

        if self.state is GameState.DYING:
            self.effect_manager.update(delta_time)

            if self.battlefield_renderer.is_player_death_finished:
                self.state = GameState.GAME_OVER
                self._finish_game()
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

        self.power_up_manager.update(delta_time)
        summoners = self.enemy_manager.update(
            delta_time,
            self.power_up_manager.enemy_speed_multiplier,
        )
        for summoner in summoners:
            self.battlefield_renderer.play_enemy_summon(summoner)
        energy_hits = self.projectile_manager.update(delta_time)
        self._resolve_energy_hits(energy_hits)
        if self.state is GameState.WAVE_BREAK:
            return
        self._handle_enemy_arrivals()
        self.effect_manager.update(delta_time)

    def _begin_wave_break(self, preserve_boss_death: bool = False) -> None:
        """Limpia la arena, anuncia el avance y espera dos segundos."""
        self.wave_manager.advance_wave()
        self.enemy_manager.clear_for_wave_break()
        self.projectile_manager.reset()
        self.battlefield_renderer.reset_enemy_animations(
            preserve_boss_death=preserve_boss_death
        )
        # Los efectos de una recompensa recién obtenida terminan durante la pausa.
        self.effect_manager.create_wave_announcement(
            self.wave_manager.current_wave
        )
        self.audio_manager.play("wave_start")
        self.active_enemy = None
        self.typed_text = ""
        self.wave_break_remaining = WAVE_BREAK_DURATION
        self.state = GameState.WAVE_BREAK
        self._block_text_input()

    def _update_wave_break(self, delta_time: float) -> None:
        """Mantiene la partida quieta hasta que pueda iniciar la ronda."""
        self.wave_break_remaining = max(
            0.0, self.wave_break_remaining - delta_time
        )
        self.effect_manager.update(delta_time)
        if self.wave_break_remaining <= 0.001:
            self.wave_break_remaining = 0.0
            self.enemy_manager.start_wave()
            self.state = GameState.PLAYING
            self._reset_caret_blink()
            self._block_text_input()

    def _activate_automatic_power_up(self, power_up: PowerUpType) -> None:
        """Aplica una recompensa automática y avisa al jugador."""

        if power_up is PowerUpType.RECOVERY:
            if self.lives < self.max_lives:
                self.lives += 1
                gained_life = True
            elif not self.bonus_heart_active:
                self.bonus_heart_active = True
                gained_life = True
            else:
                gained_life = False
            self.audio_manager.play("power_up_activate")
            if gained_life:
                self.effect_manager.create_one_up_heart(
                    PLAYER_POSITION, power_up.color
                )
            else:
                self.effect_manager.create_power_up_burst(
                    PLAYER_POSITION, power_up.color
                )
        elif power_up is PowerUpType.DOUBLE_POINTS:
            self.power_up_manager.activate_double_points()
            self.audio_manager.play("power_up_activate")
            self.effect_manager.create_power_up_burst(
                PLAYER_POSITION, power_up.color
            )

    def _activate_power_up_slot(self, slot_index: int) -> None:
        """Activa la habilidad asignada a una ranura del HUD."""

        power_up = PowerUpType.from_slot(slot_index)
        if power_up is None:
            return

        activated = False

        if power_up is PowerUpType.SLOW:
            activated = self.power_up_manager.activate_slow()
        elif power_up is PowerUpType.SHIELD:
            activated = self.power_up_manager.activate_shield()
        elif power_up is PowerUpType.EMP:
            activated = self.power_up_manager.activate_emp()
            if activated:
                self.enemy_manager.send_all_to_start()
                self.effect_manager.create_emp_pulse(
                    PLAYER_POSITION, power_up.color
                )
        elif power_up is PowerUpType.MULTISHOT:
            activated = self.power_up_manager.arm_multishot()
        if not activated:
            return

        self.audio_manager.play("power_up_activate")
        self.effect_manager.create_power_up_burst(
            PLAYER_POSITION, power_up.color
        )

    def _update_countdown(self, delta_time: float) -> None:
        """Reduce la espera y activa la partida al llegar a cero."""

        self.countdown_remaining = max(
            0.0,
            self.countdown_remaining - delta_time,
        )

        if self.countdown_remaining == 0.0:
            self.state = GameState.PLAYING
            self.showing_revive = False
            self._reset_caret_blink()
            self._block_text_input()

    def _handle_enemy_arrivals(self) -> None:
        """Resta vidas por cada enemigo que alcanza la base."""

        reached_enemies = self.enemy_manager.reached_enemies()

        # Todos desaparecen antes de resolver el daño. Así, si varios llegan
        # juntos o se agota la última vida, ninguno permanece sobre el jugador.
        for enemy in reached_enemies:
            self.enemy_manager.remove(enemy)
            self.projectile_manager.cancel_target(enemy)

        if self.active_enemy in reached_enemies:
            self.active_enemy = None
            self.typed_text = ""
            self.word_had_error = False
            self._reset_caret_blink()

        for enemy in reached_enemies:
            self.missed_words += 1
            self.combo = 0

            # Shield tiene prioridad sobre el corazón verde de Recuperación.
            if self.power_up_manager.consume_shield():
                self.audio_manager.play("power_up_activate")
                self.effect_manager.create_shield_block(
                    PLAYER_POSITION, PowerUpType.SHIELD.color
                )
                if self.save_manager.talent_level("reactive_shield"):
                    self.enemy_manager.push_nearby_enemies(
                        PLAYER_POSITION,
                        SHIELD_REACTION_RADIUS,
                        SHIELD_REACTION_DISTANCE,
                    )
                continue

            if self.bonus_heart_active:
                self.bonus_heart_active = False
                self.audio_manager.play("power_up_activate")
                self.effect_manager.create_power_up_burst(
                    PLAYER_POSITION, PowerUpType.RECOVERY.color
                )
                continue

            self.audio_manager.play("player_damage")
            self.lives -= 1
            last_breath_triggered = False
            if (
                self.lives == 1
                and not self.last_breath_used
                and self.save_manager.talent_level("last_breath")
            ):
                self.last_breath_used = True
                last_breath_triggered = True
                self.power_up_manager.trigger_emp()
                self.enemy_manager.send_all_to_start()
                self.effect_manager.create_emp_pulse(
                    PLAYER_POSITION, PowerUpType.EMP.color
                )
                self.audio_manager.play("power_up_activate")

            if self.lives <= 0:
                self.effect_manager.create_player_death(PLAYER_POSITION)
                self.battlefield_renderer.play_player_death()
                self.state = GameState.DYING
                return

            self.effect_manager.create_player_damage(PLAYER_POSITION)
            self.battlefield_renderer.play_player_damage()
            if last_breath_triggered:
                # El pulso también despeja a quienes llegaron en el mismo frame.
                break

        if reached_enemies:
            self.enemy_manager.ensure_enemy()

    def _start_new_game(
        self,
        difficulty: Difficulty | None = None,
    ) -> None:
        """Restablece el progreso y comienza una partida nueva."""

        restarting_after_game_over = self.state is GameState.GAME_OVER
        starting_from_difficulty = self.state is GameState.DIFFICULTY
        self.showing_revive = (
            restarting_after_game_over or starting_from_difficulty
        )

        if difficulty is not None:
            self.selected_difficulty = difficulty
        self.wave_manager.set_difficulty(self.selected_difficulty)

        self.completed_words = 0
        self.missed_words = 0
        self.max_lives = STARTING_LIVES + self.save_manager.talent_level("extra_life")
        self.lives = self.max_lives
        self.bonus_heart_active = False
        self.last_breath_used = False
        self.word_had_error = False
        self.run_reward_banked = False
        self.score = 0
        self.combo = 0
        self.is_new_high_score = False
        self.defeated_enemies.clear()
        self.typed_text = ""
        self.active_enemy = None
        self.typing_stats.reset()
        self.wave_manager.reset()
        self.wave_break_remaining = 0.0
        self.enemy_manager.reset()
        self.effect_manager.reset()
        self.projectile_manager.reset()
        self.power_up_manager.reset()
        if self.save_manager.talent_level("prepared_start"):
            self.power_up_manager.grant_starting_charge()
        self.battlefield_renderer.reset_enemy_animations()

        if self.showing_revive:
            # La muerte invertida comunica visualmente que comienza otra ronda.
            self.battlefield_renderer.play_player_revive()
            self.effect_manager.create_player_revive(PLAYER_POSITION)
        else:
            self.battlefield_renderer.reset_player_animation()

        self.audio_manager.play("game_start")
        self._start_countdown()

    def _start_countdown(self) -> None:
        """Inicia el tiempo de preparación con la acción congelada."""

        self.countdown_remaining = COUNTDOWN_DURATION
        self.dragging_volume_slider = False
        self.state = GameState.COUNTDOWN
        self._reset_caret_blink()
        self._block_text_input()

    def _finish_game(self) -> None:
        """Compara el resultado final con el récord almacenado."""

        if self.run_reward_banked:
            return
        self.run_reward_banked = True
        self.game_over_selection = 0
        self.audio_manager.play("game_over")
        self.is_new_high_score = self.save_manager.finish_run(
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

    def _resize_window(self, width: int, height: int) -> None:
        """Aplica un tamaño mínimo al redimensionar la ventana."""

        # En pantalla completa el sistema operativo controla las dimensiones.
        if self.is_fullscreen:
            return

        window_size = (
            max(MIN_WINDOW_WIDTH, width),
            max(MIN_WINDOW_HEIGHT, height),
        )
        self.windowed_size = window_size
        self.display_surface = pygame.display.set_mode(
            window_size,
            pygame.RESIZABLE,
        )

    def _toggle_fullscreen(self) -> None:
        """Alterna entre pantalla completa y el último tamaño de ventana."""

        try:
            if self.is_fullscreen:
                display_surface = pygame.display.set_mode(
                    self.windowed_size,
                    pygame.RESIZABLE,
                )
                target_position = self.windowed_position
            else:
                # Una ventana sin bordes ocupa el escritorio sin activar el
                # modo exclusivo que puede resultar inestable en Windows.
                self.windowed_size = self.display_surface.get_size()
                self.windowed_position = self._get_window_position()
                desktop_sizes = pygame.display.get_desktop_sizes()
                desktop_size = (
                    desktop_sizes[0]
                    if desktop_sizes
                    else self.windowed_size
                )
                display_surface = pygame.display.set_mode(
                    desktop_size,
                    pygame.NOFRAME,
                )
                target_position = (0, 0)
        except pygame.error:
            # Si el sistema rechaza el cambio, se conserva el modo actual.
            return

        self.display_surface = display_surface
        self._set_window_position(target_position)
        self.is_fullscreen = not self.is_fullscreen

        self.audio_manager.play("menu_adjust")

    @staticmethod
    def _get_window_position() -> tuple[int, int]:
        """Obtiene la posición de la ventana para poder restaurarla."""

        if sys.platform != "win32":
            return (0, 0)

        window_handle = pygame.display.get_wm_info().get("window")

        if not window_handle:
            return (0, 0)

        window_rect = wintypes.RECT()
        success = ctypes.windll.user32.GetWindowRect(
            wintypes.HWND(window_handle),
            ctypes.byref(window_rect),
        )

        if not success:
            return (0, 0)

        return (window_rect.left, window_rect.top)

    @staticmethod
    def _set_window_position(position: tuple[int, int]) -> None:
        """Mueve la ventana sin cambiar su tamaño ni robar el foco."""

        if sys.platform != "win32":
            return

        window_handle = pygame.display.get_wm_info().get("window")

        if not window_handle:
            return

        no_size = 0x0001
        no_z_order = 0x0004
        no_activate = 0x0010
        flags = no_size | no_z_order | no_activate

        ctypes.windll.user32.SetWindowPos(
            wintypes.HWND(window_handle),
            wintypes.HWND(0),
            position[0],
            position[1],
            0,
            0,
            flags,
        )

    @staticmethod
    def _is_window_maximized() -> bool:
        """Detecta la ventana maximizada para aplicar el escalado de relleno."""

        if sys.platform != "win32":
            return False

        window_handle = pygame.display.get_wm_info().get("window")
        if not window_handle:
            return False

        return bool(
            ctypes.windll.user32.IsZoomed(
                wintypes.HWND(window_handle)
            )
        )

    def _display_to_logical(
        self,
        position: tuple[int, int],
    ) -> tuple[int, int] | None:
        """Convierte un clic de la ventana a las coordenadas del lienzo."""

        display_width, display_height = self.display_surface.get_size()
        horizontal_scale = display_width / WINDOW_WIDTH
        vertical_scale = display_height / WINDOW_HEIGHT
        should_fill_display = (
            self.is_fullscreen or self._is_window_maximized()
        )
        scale = (
            max(horizontal_scale, vertical_scale)
            if should_fill_display
            else min(horizontal_scale, vertical_scale)
        )
        scaled_width = WINDOW_WIDTH * scale
        scaled_height = WINDOW_HEIGHT * scale
        offset_x = (display_width - scaled_width) / 2
        offset_y = (display_height - scaled_height) / 2
        logical_x = (position[0] - offset_x) / scale
        logical_y = (position[1] - offset_y) / scale

        if not (0 <= logical_x < WINDOW_WIDTH and 0 <= logical_y < WINDOW_HEIGHT):
            return None
        return (round(logical_x), round(logical_y))

    def _draw(self) -> None:
        """Dibuja el fotograma actual y lo presenta en la ventana."""

        menu_states = {
            GameState.MENU,
            GameState.DIFFICULTY,
            GameState.OPTIONS,
            GameState.SHOP,
            GameState.CREDITS,
            GameState.CONTACT,
        }
        help_over_menu = (
            self.state is GameState.HELP
            and self.help_return_state in menu_states
        )

        if self.state in menu_states or help_over_menu:
            # Las pantallas iniciales usan el fondo sin entidades ni rutas.
            self.battlefield_renderer.draw_menu_background()
        else:
            self.battlefield_renderer.draw(
                enemy_manager=self.enemy_manager,
                active_enemy=self.active_enemy,
                typed_text=self.typed_text,
                effect_manager=self.effect_manager,
                projectile_manager=self.projectile_manager,
                power_up_manager=self.power_up_manager,
            )

        if self.state not in menu_states and not help_over_menu:
            combo_multiplier = self._get_combo_multiplier()
            self.ui_renderer.draw_interface(
                typed_text=self.typed_text,
                caret_visible=self.caret_visible,
                score=self.score,
                combo=self.combo,
                combo_multiplier=combo_multiplier,
                combo_progress=self._get_combo_progress(),
                lives=self.lives,
                typing_stats=self.typing_stats,
                wave_manager=self.wave_manager,
                power_up_manager=self.power_up_manager,
                bonus_heart_active=self.bonus_heart_active,
                max_lives=self.max_lives,
            )
            if self.state in (
                GameState.PLAYING,
                GameState.PAUSED,
                GameState.COUNTDOWN,
                GameState.WAVE_BREAK,
            ):
                self.battlefield_renderer.draw_slow_overlay(
                    self.power_up_manager
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
            audio_volume=self.audio_manager.volume,
            audio_muted=self.audio_manager.muted,
            is_fullscreen=self.is_fullscreen,
            menu_selection=self.menu_selection,
            game_over_selection=self.game_over_selection,
            difficulty_selection=self.difficulty_selection,
            help_page=self.help_page,
            help_selection=self.help_selection,
            restarting=self.showing_revive,
            shop_points=self.save_manager.available_points,
            shop_levels=self.save_manager.talent_levels,
            shop_selection=self.shop_selection,
            shop_message=self.shop_message,
        )

        # El aviso queda sobre el HUD sin bloquear ni pausar la acción.
        if self.state in (GameState.PLAYING, GameState.WAVE_BREAK):
            self.effect_manager.draw_wave_announcement(
                self.screen,
                self.title_font,
            )

        self._present_frame()

    def _present_frame(self) -> None:
        """Escala el fotograma lógico conservando su proporción original."""

        display_width, display_height = self.display_surface.get_size()
        horizontal_scale = display_width / WINDOW_WIDTH
        vertical_scale = display_height / WINDOW_HEIGHT

        should_fill_display = (
            self.is_fullscreen or self._is_window_maximized()
        )

        if should_fill_display:
            # En pantalla completa o maximizada se rellena toda el área. El
            # exceso se recorta por igual en ambos lados del eje correspondiente.
            scale = max(horizontal_scale, vertical_scale)
            scaled_size = (
                max(1, math.ceil(WINDOW_WIDTH * scale)),
                max(1, math.ceil(WINDOW_HEIGHT * scale)),
            )
        else:
            # En ventana se conserva todo el lienzo aunque aparezcan bandas.
            scale = min(horizontal_scale, vertical_scale)
            scaled_size = (
                max(1, round(WINDOW_WIDTH * scale)),
                max(1, round(WINDOW_HEIGHT * scale)),
            )
        if scaled_size == (WINDOW_WIDTH, WINDOW_HEIGHT):
            scaled_frame = self.screen
        else:
            scaled_frame = pygame.transform.smoothscale(
                self.screen,
                scaled_size,
            )
        frame_position = (
            (display_width - scaled_size[0]) // 2,
            (display_height - scaled_size[1]) // 2,
        )

        # El desplazamiento negativo centra el recorte usado en pantalla completa.
        self.display_surface.fill(BACKGROUND_COLOR)
        self.display_surface.blit(scaled_frame, frame_position)

        # Muestra en pantalla todo lo dibujado durante este fotograma.
        pygame.display.flip()
