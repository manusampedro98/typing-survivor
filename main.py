"""Punto de entrada: por ahora solo comprueba la instalación de Pygame."""

import pygame


def main() -> None:
    """Confirma que el entorno está preparado para empezar el proyecto."""
    print(f"Typing Survivor: entorno preparado con Pygame {pygame.version.ver}.")
    print("La lógica del juego todavía no está implementada.")


if __name__ == "__main__":
    main()