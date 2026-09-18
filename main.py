"""Punto de entrada de Typing Survivor."""

from game.game import Game


def main() -> None:
    """Crea una instancia del juego e inicia su ejecución."""

    # La clase Game contiene la ventana, los eventos y el bucle principal.
    game = Game()
    game.run()


# Evita que el juego se inicie automáticamente al importar este módulo.
if __name__ == "__main__":
    main()