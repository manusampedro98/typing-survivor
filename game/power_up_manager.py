"""Gestión de los power-ups obtenidos durante la partida."""

from random import random

from game.settings import (
    SLOW_ENEMY_SPEED_MULTIPLIER,
    SLOW_POWER_UP_DROP_CHANCE,
    SLOW_POWER_UP_DURATION,
)


class PowerUpManager:
    """Controla la carga y la duración de la ralentización."""

    def __init__(self) -> None:
        """Comienza sin una carga disponible ni un efecto activo."""

        self.slow_charge_available = False
        self.slow_time_remaining = 0.0

    @property
    def is_slow_active(self) -> bool:
        """Indica si los enemigos deben moverse más despacio."""

        return self.slow_time_remaining > 0.0

    @property
    def enemy_speed_multiplier(self) -> float:
        """Devuelve el factor que se aplicará al movimiento enemigo."""

        if self.is_slow_active:
            return SLOW_ENEMY_SPEED_MULTIPLIER
        return 1.0

    def try_grant_slow_charge(self) -> bool:
        """Intenta conceder una carga y comunica si se ha obtenido."""

        # Solo se almacena una carga, aunque el efecto actual siga activo.
        if self.slow_charge_available:
            return False

        if random() >= SLOW_POWER_UP_DROP_CHANCE:
            return False

        self.slow_charge_available = True
        return True

    def activate_slow(self) -> bool:
        """Consume una carga si la ralentización puede comenzar."""

        if not self.slow_charge_available or self.is_slow_active:
            return False

        self.slow_charge_available = False
        self.slow_time_remaining = SLOW_POWER_UP_DURATION
        return True

    def update(self, delta_time: float) -> None:
        """Reduce el tiempo restante del efecto activo."""

        if self.is_slow_active:
            self.slow_time_remaining = max(
                0.0,
                self.slow_time_remaining - delta_time,
            )

    def reset(self) -> None:
        """Elimina la carga y el efecto de la partida anterior."""

        self.slow_charge_available = False
        self.slow_time_remaining = 0.0
