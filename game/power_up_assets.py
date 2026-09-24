"""Carga compartida de los iconos de potenciadores."""

from pathlib import Path

import pygame

from game.power_up_type import PowerUpType


ICON_DIRECTORY = (
    Path(__file__).resolve().parent.parent
    / "assets" / "images" / "ui" / "power_up_icons"
)
ICON_FILENAMES = {
    PowerUpType.SLOW: "slow_powerup_icon.png",
    PowerUpType.SHIELD: "shield_powerup_icon.png",
    PowerUpType.EMP: "emp_powerup_icon.png",
    PowerUpType.MULTISHOT: "multishot_powerup_icon.png",
}


def load_power_up_icon(power_up: PowerUpType, max_size: int) -> pygame.Surface | None:
    """Recorta los márgenes transparentes y conserva las proporciones."""

    filename = ICON_FILENAMES.get(power_up)
    if filename is None:
        return _draw_automatic_icon(power_up, max_size)
    try:
        image = pygame.image.load(str(ICON_DIRECTORY / filename)).convert_alpha()
        visible = image.get_bounding_rect(min_alpha=8)
        if not visible:
            return None
        image = image.subsurface(visible).copy()
        scale = min(max_size / image.get_width(), max_size / image.get_height())
        return pygame.transform.smoothscale(
            image,
            (
                max(1, round(image.get_width() * scale)),
                max(1, round(image.get_height() * scale)),
            ),
        )
    except (pygame.error, OSError):
        return None


def _draw_automatic_icon(
    power_up: PowerUpType, size: int
) -> pygame.Surface | None:
    """Representa los dos premios automáticos mientras no tengan PNG propios."""

    if power_up not in (PowerUpType.RECOVERY, PowerUpType.DOUBLE_POINTS):
        return None
    canvas = pygame.Surface((size, size), pygame.SRCALPHA)
    if power_up is PowerUpType.RECOVERY:
        def heart(color: tuple[int, int, int], inset: int) -> None:
            radius = max(2, round(size * 0.19) - inset)
            left = (round(size * 0.36), round(size * 0.39))
            right = (round(size * 0.64), round(size * 0.39))
            pygame.draw.circle(canvas, color, left, radius)
            pygame.draw.circle(canvas, color, right, radius)
            pygame.draw.polygon(canvas, color, (
                (left[0] - radius, left[1]),
                (right[0] + radius, right[1]),
                (round(size * 0.5), round(size * 0.83) - inset),
            ))

        heart((12, 44, 35), 0)
        heart((82, 226, 145), max(1, round(size * 0.07)))
        pygame.draw.circle(canvas, (219, 255, 232),
                           (round(size * 0.32), round(size * 0.33)),
                           max(1, round(size * 0.06)))
    else:
        for center, fill in (
            ((round(size * 0.61), round(size * 0.39)), (225, 139, 33)),
            ((round(size * 0.40), round(size * 0.61)), (255, 204, 67)),
        ):
            radius = round(size * 0.27)
            pygame.draw.circle(canvas, (50, 34, 27), center, radius + 2)
            pygame.draw.circle(canvas, fill, center, radius)
            pygame.draw.circle(canvas, (255, 237, 153), center,
                               max(1, radius - 4), width=2)
            pygame.draw.circle(canvas, (255, 255, 214),
                               (center[0] - radius // 3,
                                center[1] - radius // 3),
                               max(1, round(size * 0.05)))
    return canvas
