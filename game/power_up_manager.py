"""Gestión de cargas y estados temporales de los potenciadores."""

from random import choice, random

from game.power_up_type import PowerUpType
from game.talents import PRECISION_SLOW_DURATIONS, PRECISION_SLOW_SPEED_MULTIPLIER
from game.settings import (
    DOUBLE_POINTS_DURATION,
    EMP_STUN_DURATION,
    POWER_UP_DROP_CHANCE,
    SLOW_ENEMY_SPEED_MULTIPLIER,
    SLOW_POWER_UP_DURATION,
)


class PowerUpManager:
    """Controla cuatro ranuras y dos efectos que se activan al obtenerse."""

    def __init__(self) -> None:
        """Comienza sin cargas ni habilidades activas."""

        self.charges = {
            power_up: False
            for power_up in PowerUpType if not power_up.is_automatic
        }
        self.slow_time_remaining = 0.0
        self.emp_stun_time_remaining = 0.0
        self.double_points_time_remaining = 0.0
        self.precision_slow_time_remaining = 0.0
        self.shield_active = False
        self.multishot_armed = False

    @property
    def is_slow_active(self) -> bool:
        """Indica si los enemigos deben moverse más despacio."""

        return self.slow_time_remaining > 0.0

    @property
    def is_emp_stun_active(self) -> bool:
        """Indica si el Pulso EMP mantiene inmóviles a los enemigos."""

        return self.emp_stun_time_remaining > 0.0

    @property
    def is_double_points_active(self) -> bool:
        """Indica si las palabras conceden el doble de puntos."""

        return self.double_points_time_remaining > 0.0

    @property
    def enemy_speed_multiplier(self) -> float:
        """Devuelve el factor que se aplicará al movimiento enemigo."""

        if self.is_emp_stun_active:
            return 0.0
        speed = SLOW_ENEMY_SPEED_MULTIPLIER if self.is_slow_active else 1.0
        if self.precision_slow_time_remaining > 0.0:
            speed = min(speed, PRECISION_SLOW_SPEED_MULTIPLIER)
        return speed

    @property
    def score_multiplier(self) -> int:
        """Devuelve el multiplicador temporal de puntuación."""

        return 2 if self.is_double_points_active else 1

    def grant_starting_charge(self) -> PowerUpType:
        """Prepara un potenciador manual aleatorio al empezar una partida."""

        power_up = choice(tuple(self.charges))
        self.charges[power_up] = True
        return power_up

    def trigger_precision_slow(self, level: int) -> None:
        """Ralentiza brevemente a todos tras una palabra sin errores."""

        if 1 <= level <= len(PRECISION_SLOW_DURATIONS):
            self.precision_slow_time_remaining = max(
                self.precision_slow_time_remaining,
                PRECISION_SLOW_DURATIONS[level - 1],
            )

    def trigger_emp(self) -> None:
        """Activa el mismo aturdimiento del EMP sin consumir una carga."""

        self.emp_stun_time_remaining = EMP_STUN_DURATION

    def has_charge(self, power_up: PowerUpType) -> bool:
        """Consulta si una ranura contiene una carga preparada."""

        return self.charges.get(power_up, False)

    def try_grant_charge(self, chance_multiplier: float = 1.0) -> PowerUpType | None:
        """Sortea una carga manual o un efecto automático al obtener un drop."""

        if random() >= POWER_UP_DROP_CHANCE * chance_multiplier:
            return None

        # Los seis tipos conservan la misma probabilidad de selección.
        granted_power_up = choice(tuple(PowerUpType))
        if not granted_power_up.is_automatic:
            if self.charges[granted_power_up]:
                return None
            self.charges[granted_power_up] = True
        return granted_power_up

    def activate_slow(self) -> bool:
        """Consume Ralentización si su efecto no está activo."""

        if self.is_slow_active:
            return False
        if not self._consume_charge(PowerUpType.SLOW):
            return False

        self.slow_time_remaining = SLOW_POWER_UP_DURATION
        return True

    def activate_shield(self) -> bool:
        """Prepara Shield para absorber una llegada enemiga."""

        if self.shield_active:
            return False
        if not self._consume_charge(PowerUpType.SHIELD):
            return False

        self.shield_active = True
        return True

    def consume_shield(self) -> bool:
        """Retira Shield y comunica si ha bloqueado daño."""

        if not self.shield_active:
            return False
        self.shield_active = False
        return True

    def activate_emp(self) -> bool:
        """Consume Pulso EMP e inicia dos segundos de inmovilización."""

        if self.is_emp_stun_active:
            return False
        if not self._consume_charge(PowerUpType.EMP):
            return False

        self.trigger_emp()
        return True

    def arm_multishot(self) -> bool:
        """Prepara el rebote del siguiente proyectil válido."""

        if self.multishot_armed:
            return False
        if not self._consume_charge(PowerUpType.MULTISHOT):
            return False

        self.multishot_armed = True
        return True

    def consume_multishot(self) -> bool:
        """Consume Multishot cuando existen objetivos secundarios."""

        if not self.multishot_armed:
            return False
        self.multishot_armed = False
        return True

    def activate_double_points(self) -> None:
        """Activa o renueva el efecto automático de puntos dobles."""

        self.double_points_time_remaining = DOUBLE_POINTS_DURATION

    def get_active_time(self, power_up: PowerUpType) -> float:
        """Devuelve el tiempo restante de las habilidades temporales."""

        if power_up is PowerUpType.SLOW:
            return self.slow_time_remaining
        if power_up is PowerUpType.EMP:
            return self.emp_stun_time_remaining
        if power_up is PowerUpType.DOUBLE_POINTS:
            return self.double_points_time_remaining
        return 0.0

    def is_active(self, power_up: PowerUpType) -> bool:
        """Consulta el estado activo o preparado de una habilidad."""

        if power_up is PowerUpType.SLOW:
            return self.is_slow_active
        if power_up is PowerUpType.SHIELD:
            return self.shield_active
        if power_up is PowerUpType.EMP:
            return self.is_emp_stun_active
        if power_up is PowerUpType.MULTISHOT:
            return self.multishot_armed
        if power_up is PowerUpType.DOUBLE_POINTS:
            return self.is_double_points_active
        return False

    def update(self, delta_time: float) -> None:
        """Reduce la duración de los efectos temporales."""

        self.slow_time_remaining = max(
            0.0,
            self.slow_time_remaining - delta_time,
        )
        self.emp_stun_time_remaining = max(
            0.0,
            self.emp_stun_time_remaining - delta_time,
        )
        self.double_points_time_remaining = max(
            0.0,
            self.double_points_time_remaining - delta_time,
        )
        self.precision_slow_time_remaining = max(
            0.0,
            self.precision_slow_time_remaining - delta_time,
        )

    def reset(self) -> None:
        """Elimina cargas y efectos pertenecientes a la partida anterior."""

        for power_up in self.charges:
            self.charges[power_up] = False
        self.slow_time_remaining = 0.0
        self.emp_stun_time_remaining = 0.0
        self.double_points_time_remaining = 0.0
        self.precision_slow_time_remaining = 0.0
        self.shield_active = False
        self.multishot_armed = False

    def _consume_charge(self, power_up: PowerUpType) -> bool:
        """Consume una carga concreta cuando está disponible."""

        if not self.charges[power_up]:
            return False
        self.charges[power_up] = False
        return True
