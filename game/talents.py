"""Catálogo y valores de las mejoras permanentes de la tienda."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Talent:
    key: str
    name: str
    description: str
    base_cost: int
    max_level: int = 1
    cost_step: int = 0

    def next_cost(self, current_level: int) -> int | None:
        """Precio del próximo nivel; None si ya está completo."""

        if current_level >= self.max_level:
            return None
        return self.base_cost + self.cost_step * current_level


TALENTS = (
    Talent("extra_life", "Vida adicional", "+1 al máximo de corazones.", 20000),
    Talent("prepared_start", "Comienzo preparado", "Empieza con un potenciador cargado.", 3000),
    Talent("more_drops", "Más hallazgos", "+20 % de probabilidad de potenciador.", 7000),
    Talent("precision_pulse", "Pulso certero", "Palabras perfectas frenan a todos.", 4000, 3, 3000),
    Talent("armor_break", "Rompeescudos", "El blindado retrocede al perder escudo.", 5000),
    Talent("reactive_shield", "Shield reactivo", "Al bloquear, empuja enemigos cercanos.", 7000),
    Talent("multishot_plus", "Multishot mejorado", "+1 rebote por nivel (máximo 5).", 5000, 5, 3000),
    Talent("last_breath", "Último aliento", "Al quedarte con 1 vida, EMP una vez.", 12000),
)
TALENTS_BY_KEY = {talent.key: talent for talent in TALENTS}

PRECISION_SLOW_DURATIONS = (1.0, 1.5, 2.0)
PRECISION_SLOW_SPEED_MULTIPLIER = 0.75
DROP_BONUS_MULTIPLIER = 1.20
ARMORED_KNOCKBACK_DISTANCE = 95.0
SHIELD_REACTION_RADIUS = 240.0
SHIELD_REACTION_DISTANCE = 120.0
