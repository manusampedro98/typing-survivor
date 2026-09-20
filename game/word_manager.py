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
    """Carga la lista y proporciona palabras para los enemigos."""

    def __init__(self, words_file: Path = DEFAULT_WORDS_FILE) -> None:
        """Carga las palabras disponibles durante la partida."""

        self.words = self._load_words(words_file)
        self.last_selected_word: str | None = None

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

    def choose_word(
        self,
        excluded_words: set[str] | None = None,
    ) -> str:
        """Selecciona una palabra que no esté siendo utilizada en pantalla."""

        excluded_words = excluded_words or set()

        # Evita duplicados visibles y repeticiones consecutivas cuando sea posible.
        available_words = [
            word
            for word in self.words
            if word not in excluded_words
            and word != self.last_selected_word
        ]

        # Si quedan pocas palabras, se prioriza no duplicar las visibles.
        fallback_words = [
            word
            for word in self.words
            if word not in excluded_words
        ]
        selected_word = choice(
            available_words
            or fallback_words
            or self.words
        )
        self.last_selected_word = selected_word
        return selected_word
