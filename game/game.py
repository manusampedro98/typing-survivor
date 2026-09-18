"""Controlador principal de Typing Survivor."""

import pygame

from game.settings import (
    BACKGROUND_COLOR,
    FPS,
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

        # Surface principal sobre la que se dibujarán todos los elementos.
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)

        # El reloj controla la velocidad máxima del bucle principal.
        self.clock = pygame.time.Clock()

        # Esta variable determina cuándo debe finalizar la aplicación.
        self.running = True

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
            # Garantiza que Pygame libere sus recursos incluso si ocurre un error.
            pygame.quit()

    def _handle_events(self) -> None:
        """Procesa los eventos generados por el sistema y por el usuario."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def _update(self) -> None:
        """Actualiza el estado de los elementos del juego."""

        # Este método se completará cuando añadamos las primeras mecánicas.
        pass

    def _draw(self) -> None:
        """Dibuja el fotograma actual y lo presenta en la ventana."""

        # Limpia el contenido del fotograma anterior.
        self.screen.fill(BACKGROUND_COLOR)

        # Muestra en pantalla todo lo dibujado durante este fotograma.
        pygame.display.flip()