"""Punto de entrada de Typing Survivor."""

import pygame


# Configuración general de la ventana.
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Color RGB utilizado para limpiar el fotograma antes de dibujar.
BACKGROUND_COLOR = (16, 18, 27)


def main() -> None:
    """Inicia Pygame y mantiene activo el bucle principal del juego."""

    # Inicializa los módulos internos de Pygame.
    pygame.init()

    # Crea la ventana donde se dibujarán todos los elementos del juego.
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Typing Survivor")

    # El reloj permite limitar la velocidad del juego a un número estable de FPS.
    clock = pygame.time.Clock()
    running = True

    # Cada repetición del bucle representa un fotograma del juego.
    while running:
        # Procesa los eventos generados por el sistema y por el usuario.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Limpia el contenido del fotograma anterior.
        screen.fill(BACKGROUND_COLOR)

        # Presenta en la ventana todo lo dibujado durante este fotograma.
        pygame.display.flip()

        # Evita que el bucle se ejecute a más de 60 fotogramas por segundo.
        clock.tick(FPS)

    # Libera los recursos utilizados por Pygame al cerrar el juego.
    pygame.quit()


if __name__ == "__main__":
    main()