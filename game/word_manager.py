"""Carga y selecciona las palabras utilizadas durante la partida."""

from pathlib import Path
from random import choice


# Construye una ruta independiente del lugar desde el que se ejecute el juego.
DEFAULT_WORDS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "words.txt"
)


class WordManager:
    """Gestiona la lista de palabras y selecciona el objetivo actual."""

    def __init__(self, words_file: Path = DEFAULT_WORDS_FILE) -> None:
        """Carga las palabras y selecciona el primer objetivo."""

        self.words = self._load_words(words_file)
        self.current_word = self.next_word()

    @staticmethod
    def _load_words(words_file: Path) -> list[str]:
        """Lee el archivo y devuelve únicamente las líneas con contenido."""

        # UTF-8 permite utilizar palabras con tildes y otros caracteres.
        file_content = words_file.read_text(encoding="utf-8")

        words = [
            line.strip().lower()
            for line in file_content.splitlines()
            if line.strip()
        ]

        # Detiene el inicio con un mensaje claro si el archivo está vacío.
        if not words:
            raise ValueError(
                f"No se encontraron palabras en {words_file}."
            )

        return words

    def next_word(self) -> str:
        """Selecciona una palabra distinta de la anterior cuando sea posible."""

        previous_word = getattr(self, "current_word", None)

        # Evita repetir consecutivamente el mismo objetivo si hay alternativas.
        available_words = [
            word
            for word in self.words
            if word != previous_word
        ]

        self.current_word = choice(available_words or self.words)
        return self.current_word
