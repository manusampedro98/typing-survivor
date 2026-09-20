"""Tipos de enemigos disponibles en Typing Survivor."""

from enum import Enum


class EnemyType(Enum):
    """Identifica cada variante y sus nombres para la interfaz."""

    NORMAL = ("NORMAL", "Normales")
    FAST = ("RÁPIDO", "Rápidos")

    def __init__(self, display_name: str, plural_name: str) -> None:
        """Guarda los textos usados al mostrar el tipo y su contador."""

        self.display_name = display_name
        self.plural_name = plural_name
