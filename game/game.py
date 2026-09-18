"""Controlador principal de Typing Survivor."""

import pygame

from game.word_manager import WordManager
from game.settings import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    BODY_FONT_SIZE,
    BORDER_COLOR,
    CARET_BLINK_INTERVAL,
    CARET_HEIGHT,
    CARET_WIDTH,
    CORRECT_COLOR,
    FPS,
    INCORRECT_COLOR,
    INPUT_BOX_HEIGHT,
    INPUT_BOX_WIDTH,
    INPUT_HORIZONTAL_PADDING,
    KEY_REPEAT_DELAY,
    KEY_REPEAT_INTERVAL,
    MAX_INPUT_LENGTH,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
    SMALL_FONT_SIZE,
    TARGET_FONT_SIZE,
    TEXT_COLOR,
    TITLE_FONT_SIZE,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)


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

        # Registra el progreso básico de la sesión actual.
        self.completed_words = 0

        # Almacena temporalmente los caracteres escritos por el jugador.
        self.typed_text = ""

        # Estado utilizado para hacer parpadear el cursor de escritura.
        self.caret_visible = True
        self.caret_last_toggle = pygame.time.get_ticks()

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
                self._handle_events()
                self._update()
                self._draw()

                # Mantiene una velocidad estable y evita consumo innecesario de CPU.
                self.clock.tick(FPS)
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

            elif event.type == pygame.TEXTINPUT:
                self._append_text(event.text)

    def _handle_control_key(self, event: pygame.event.Event) -> None:
        """Gestiona las teclas que controlan la aplicación o editan el texto."""

        if event.key == pygame.K_ESCAPE:
            self.running = False

        elif event.key == pygame.K_BACKSPACE:
            # Evita modificar el texto si el campo ya está vacío.
            if self.typed_text:
                self.typed_text = self.typed_text[:-1]
                self._reset_caret_blink()

    def _append_text(self, new_text: str) -> None:
        """Añade caracteres imprimibles sin superar el límite permitido."""

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
            self.typed_text += text_to_add
            self._reset_caret_blink()

            if self.typed_text == self.word_manager.current_word:
                self._complete_current_word()

    def _complete_current_word(self) -> None:
        """Registra el acierto y prepara el siguiente objetivo."""

        self.completed_words += 1
        self.word_manager.next_word()
        self.typed_text = ""
        self._reset_caret_blink()

    def _update(self) -> None:
        """Actualiza los elementos que cambian con el paso del tiempo."""

        current_time = pygame.time.get_ticks()

        # Alterna la visibilidad del cursor cada cierto número de milisegundos.
        if current_time - self.caret_last_toggle >= CARET_BLINK_INTERVAL:
            self.caret_visible = not self.caret_visible
            self.caret_last_toggle = current_time


    def _reset_caret_blink(self) -> None:
        """Muestra el cursor inmediatamente después de editar el texto."""

        self.caret_visible = True
        self.caret_last_toggle = pygame.time.get_ticks()

    def _draw(self) -> None:
        """Dibuja el fotograma actual y lo presenta en la ventana."""

        # Limpia el contenido del fotograma anterior.
        self.screen.fill(BACKGROUND_COLOR)

        self._draw_interface()

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
            "Retroceso: borrar  |  Esc: cerrar",
            True,
            MUTED_TEXT_COLOR,
        )
        help_rect = help_surface.get_rect(
            center=(WINDOW_WIDTH // 2, input_box.bottom + 45)
        )
        self.screen.blit(help_surface, help_rect)

    def _draw_target_word(self) -> None:
        """Dibuja la palabra objetivo y compara cada carácter escrito."""

        label_surface = self.small_font.render(
            "PALABRA OBJETIVO",
            True,
            MUTED_TEXT_COLOR,
        )
        label_rect = label_surface.get_rect(
            center=(WINDOW_WIDTH // 2, 255)
        )
        self.screen.blit(label_surface, label_rect)

        character_surfaces = []

        # Asigna un color a cada carácter según el progreso del jugador.
        for index, character in enumerate(self.word_manager.current_word):
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
        character_x = (WINDOW_WIDTH - total_width) // 2

        # Dibuja las letras una junto a otra conservando sus colores.
        for character_surface in character_surfaces:
            character_rect = character_surface.get_rect(
                midleft=(character_x, 305)
            )
            self.screen.blit(character_surface, character_rect)
            character_x += character_surface.get_width()

    def _draw_progress(self) -> None:
        """Muestra el número de palabras completadas en la sesión."""

        progress_surface = self.small_font.render(
            f"Palabras completadas: {self.completed_words}",
            True,
            MUTED_TEXT_COLOR,
        )
        progress_rect = progress_surface.get_rect(
            topright=(WINDOW_WIDTH - 30, 30)
        )
        self.screen.blit(progress_surface, progress_rect)
