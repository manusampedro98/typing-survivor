"""Identificadores y presentación de los potenciadores disponibles."""

from enum import Enum


class PowerUpType(Enum):
    """Relaciona cada habilidad con su ranura, nombre y color."""

    SLOW = (0, "RALENTIZACIÓN", (65, 202, 255))
    SHIELD = (1, "SHIELD", (255, 179, 54))
    EMP = (2, "PULSO EMP", (180, 105, 255))
    MULTISHOT = (3, "MULTISHOT", (255, 150, 55))
    RECOVERY = (None, "RECUPERACIÓN", (80, 220, 140))
    DOUBLE_POINTS = (None, "DOBLE PUNTUACIÓN", (255, 205, 65))

    def __init__(
        self,
        slot_index: int | None,
        display_name: str,
        color: tuple[int, int, int],
    ) -> None:
        self.slot_index = slot_index
        self.display_name = display_name
        self.color = color

    @property
    def is_automatic(self) -> bool:
        return self.slot_index is None

    @classmethod
    def from_slot(cls, slot_index: int) -> "PowerUpType | None":
        """Obtiene el potenciador asignado a una tecla numérica."""

        return next(
            (
                power_up
                for power_up in cls
                if power_up.slot_index == slot_index
            ),
            None,
        )
