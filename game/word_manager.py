"""Carga y selecciona las palabras utilizadas durante la partida."""

from pathlib import Path
from random import choice

from game.enemy_type import EnemyType
from game.settings import BOSS_WAVE_INTERVAL, BOSS_WORD_START_LENGTH


# Construye una ruta independiente del lugar desde el que se ejecute el juego.
DEFAULT_WORDS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "words.txt"
)
DEFAULT_SKELETON_WORDS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "skeleton_words.txt"
)


class WordManager:
    """Carga la lista y proporciona palabras para los enemigos."""

    def __init__(
        self,
        words_file: Path = DEFAULT_WORDS_FILE,
        skeleton_words_file: Path = DEFAULT_SKELETON_WORDS_FILE,
    ) -> None:
        """Carga las palabras disponibles durante la partida."""

        self.words = self._load_words(words_file)
        self.skeleton_words = self._load_words(skeleton_words_file)
        if any(len(word) != 3 for word in self.skeleton_words):
            raise ValueError("Las palabras de esqueletos deben tener 3 letras.")
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

        return self._choose_from_pool(self.words, excluded_words)

    def choose_skeleton_word(
        self,
        excluded_words: set[str] | None = None,
    ) -> str:
        """Elige una palabra de exactamente tres letras."""

        return self._choose_from_pool(self.skeleton_words, excluded_words)

    def choose_for_enemy(
        self,
        enemy_type: EnemyType,
        wave_number: int,
        excluded_words: set[str] | None = None,
    ) -> str:
        """Aplica el límite de longitud propio de cada clase."""

        if enemy_type is EnemyType.SKELETON:
            return self.choose_skeleton_word(excluded_words)
        if enemy_type is EnemyType.FAST:
            pool = [word for word in self.words if len(word) <= 4]
        elif enemy_type in (
            EnemyType.NORMAL, EnemyType.GOBLIN, EnemyType.ARMORED
        ):
            pool = [word for word in self.words if len(word) <= 5]
        elif enemy_type is EnemyType.NECROMANCER:
            pool = [word for word in self.words if 6 <= len(word) <= 7]
        elif enemy_type is EnemyType.BOSS:
            target_length = BOSS_WORD_START_LENGTH + max(
                0, wave_number // BOSS_WAVE_INTERVAL - 1
            )
            pool = [
                word for word in self.words if len(word) == target_length
            ]
            if not pool:
                pool = self._build_boss_compounds(target_length)
        else:
            raise ValueError(f"Tipo de enemigo sin vocabulario: {enemy_type}")
        if not pool:
            raise ValueError(f"No hay palabras para {enemy_type.display_name}")
        return self._choose_from_pool(pool, excluded_words)

    def _build_boss_compounds(self, target_length: int) -> list[str]:
        """Compone desafíos de longitud exacta al agotarse el diccionario."""

        compounds: set[str] = set()
        for _ in range(40):
            remaining = target_length
            parts: list[str] = []
            while remaining:
                options = [
                    word for word in self.words
                    if len(word) <= remaining
                    and remaining - len(word) not in (1, 2, 3)
                ]
                if not options:
                    break
                # Prioriza pocas piezas largas para las rondas extremas.
                longest = max(map(len, options))
                long_options = [
                    word for word in options
                    if len(word) >= max(4, longest - 4)
                ]
                part = choice(long_options)
                parts.append(part)
                remaining -= len(part)
            if remaining == 0:
                compounds.add("".join(parts))
        if not compounds:
            raise ValueError(
                f"No se puede crear una palabra de {target_length} letras."
            )
        return sorted(compounds)

    def _choose_from_pool(
        self,
        pool: list[str],
        excluded_words: set[str] | None,
    ) -> str:
        excluded_words = excluded_words or set()
        compatible_words = [
            word for word in pool
            if word not in excluded_words
            and all(
                not word.startswith(active) and not active.startswith(word)
                for active in excluded_words
            )
        ]
        available_words = [
            word for word in compatible_words
            if word != self.last_selected_word
        ]
        fallback_words = [
            word for word in pool if word not in excluded_words
        ]
        selected_word = choice(
            available_words or compatible_words or fallback_words or pool
        )
        self.last_selected_word = selected_word
        return selected_word
