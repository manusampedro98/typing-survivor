"""Carga y guardado del mejor resultado obtenido por el jugador."""

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path


def _get_default_save_file() -> Path:
    """Construye una ruta de datos local independiente del repositorio."""

    local_app_data = os.getenv("LOCALAPPDATA")

    if local_app_data:
        return (
            Path(local_app_data)
            / "TypingSurvivor"
            / "save_data.json"
        )

    # Mantiene un destino válido fuera de Windows.
    return Path.home() / ".typing-survivor" / "save_data.json"


DEFAULT_SAVE_FILE = _get_default_save_file()


@dataclass
class HighScore:
    """Datos conservados de la partida con mayor puntuación."""

    score: int = 0
    wave: int = 0
    words_per_minute: float = 0.0
    accuracy: float = 0.0


class SaveManager:
    """Gestiona la lectura y escritura segura del récord local."""

    def __init__(self, save_file: Path = DEFAULT_SAVE_FILE) -> None:
        """Carga el récord existente o utiliza valores iniciales."""

        self.save_file = save_file
        self.high_score = self._load()

    def update_high_score(
        self,
        score: int,
        wave: int,
        words_per_minute: float,
        accuracy: float,
    ) -> bool:
        """Guarda los resultados si superan la puntuación anterior."""

        if score <= self.high_score.score:
            return False

        self.high_score = HighScore(
            score=max(0, score),
            wave=max(0, wave),
            words_per_minute=max(0.0, words_per_minute),
            accuracy=min(100.0, max(0.0, accuracy)),
        )
        self._save()
        return True

    def _load(self) -> HighScore:
        """Lee y valida los datos sin impedir el inicio si están dañados."""

        try:
            saved_data = json.loads(
                self.save_file.read_text(encoding="utf-8")
            )
            return HighScore(
                score=max(0, int(saved_data.get("score", 0))),
                wave=max(0, int(saved_data.get("wave", 0))),
                words_per_minute=max(
                    0.0,
                    float(saved_data.get("words_per_minute", 0.0)),
                ),
                accuracy=min(
                    100.0,
                    max(0.0, float(saved_data.get("accuracy", 0.0))),
                ),
            )
        except (
            FileNotFoundError,
            json.JSONDecodeError,
            OSError,
            TypeError,
            ValueError,
        ):
            return HighScore()

    def _save(self) -> None:
        """Escribe primero un archivo temporal y después lo reemplaza."""

        temporary_file = self.save_file.with_suffix(".tmp")

        try:
            self.save_file.parent.mkdir(parents=True, exist_ok=True)
            temporary_file.write_text(
                json.dumps(asdict(self.high_score), indent=4),
                encoding="utf-8",
            )
            temporary_file.replace(self.save_file)
        except OSError:
            # Un fallo de guardado no debe cerrar una partida terminada.
            try:
                temporary_file.unlink(missing_ok=True)
            except OSError:
                pass
