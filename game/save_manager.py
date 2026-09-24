"""Persistencia del récord, puntos disponibles y talentos adquiridos."""

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path

from game.talents import TALENTS, TALENTS_BY_KEY


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
    """Gestiona los datos persistentes del jugador en un único guardado."""

    def __init__(self, save_file: Path = DEFAULT_SAVE_FILE) -> None:
        """Carga los datos existentes o utiliza valores iniciales."""

        self.save_file = save_file
        self.high_score = self._load()
        self.available_points, self.talent_levels = self._load_store()

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

    def finish_run(
        self, score: int, wave: int, words_per_minute: float, accuracy: float
    ) -> bool:
        """Ingresa los puntos de la partida y conserva el récord independiente."""

        new_high_score = score > self.high_score.score
        if new_high_score:
            self.high_score = HighScore(
                score=max(0, score),
                wave=max(0, wave),
                words_per_minute=max(0.0, words_per_minute),
                accuracy=min(100.0, max(0.0, accuracy)),
            )
        self.available_points += max(0, score)
        if new_high_score or score > 0:
            self._save()
        return new_high_score

    def talent_level(self, key: str) -> int:
        """Devuelve el nivel permanente adquirido de un talento."""

        return self.talent_levels.get(key, 0)

    def purchase_talent(self, key: str) -> bool:
        """Descuenta el precio y guarda la mejora si puede comprarse."""

        talent = TALENTS_BY_KEY.get(key)
        if talent is None:
            return False
        current_level = self.talent_level(key)
        cost = talent.next_cost(current_level)
        if cost is None or self.available_points < cost:
            return False
        self.available_points -= cost
        self.talent_levels[key] = current_level + 1
        if not self._save():
            self.available_points += cost
            self.talent_levels[key] = current_level
            return False
        return True

    def _load_store(self) -> tuple[int, dict[str, int]]:
        """Lee saldo y niveles sin exigirlos a los guardados anteriores."""

        levels = {talent.key: 0 for talent in TALENTS}
        try:
            data = json.loads(self.save_file.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return 0, levels
            points = max(0, int(data.get("available_points", 0)))
            saved_levels = data.get("talents", {})
            if isinstance(saved_levels, dict):
                for talent in TALENTS:
                    try:
                        value = int(saved_levels.get(talent.key, 0))
                    except (TypeError, ValueError):
                        continue
                    levels[talent.key] = max(0, min(talent.max_level, value))
            return points, levels
        except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
            return 0, levels

    def _load(self) -> HighScore:
        """Lee y valida los datos sin impedir el inicio si están dañados."""

        try:
            saved_data = json.loads(
                self.save_file.read_text(encoding="utf-8")
            )
            if not isinstance(saved_data, dict):
                return HighScore()
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

    def _save(self) -> bool:
        """Escribe primero un archivo temporal y después lo reemplaza."""

        temporary_file = self.save_file.with_suffix(".tmp")

        try:
            self.save_file.parent.mkdir(parents=True, exist_ok=True)
            temporary_file.write_text(
                json.dumps({
                    **asdict(self.high_score),
                    "available_points": self.available_points,
                    "talents": self.talent_levels,
                }, indent=4),
                encoding="utf-8",
            )
            temporary_file.replace(self.save_file)
            return True
        except OSError:
            # Un fallo de guardado no debe cerrar una partida terminada.
            try:
                temporary_file.unlink(missing_ok=True)
            except OSError:
                pass
            return False
