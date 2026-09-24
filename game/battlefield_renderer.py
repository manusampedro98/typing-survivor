"""Representación visual del campo de batalla."""

from pathlib import Path
from math import cos, sin, tau
from random import Random

import pygame

from game.effects import EffectManager
from game.enemy import Enemy
from game.enemy_type import EnemyType
from game.enemy_manager import EnemyManager
from game.enemy_renderer import EnemyRenderer
from game.player_renderer import PlayerRenderer
from game.power_up_assets import load_power_up_icon
from game.power_up_manager import PowerUpManager
from game.power_up_type import PowerUpType
from game.projectile_manager import ProjectileManager
from game.settings import (
    ARENA_BACKGROUND_DARKEN_ALPHA,
    BACKGROUND_COLOR,
    CORRECT_COLOR,
    INCORRECT_COLOR,
    MUTED_TEXT_COLOR,
    PLAYER_POSITION,
    POINTS_PER_CHARACTER,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


DEFAULT_BACKGROUND_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "images"
    / "backgrounds"
    / "arena_background.png"
)


class BattlefieldRenderer:
    """Dibuja elementos de combate sin modificar su estado."""

    def __init__(
        self,
        screen: pygame.Surface,
        target_font: pygame.font.Font,
        body_font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        """Recibe la superficie y las fuentes creadas por el juego."""

        self.screen = screen
        self.target_font = target_font
        self.body_font = body_font
        self.small_font = small_font

        # El jugador mantiene su propia carga de sprites y reloj de animación.
        self.player_renderer = PlayerRenderer(screen, body_font)
        self.enemy_renderer = EnemyRenderer()

        # El fondo se carga y escala una sola vez, no en cada fotograma.
        self.background = self._load_background(DEFAULT_BACKGROUND_PATH)
        self.background_tint = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA,
        )
        self.background_tint.fill(
            (0, 0, 0, ARENA_BACKGROUND_DARKEN_ALPHA)
        )
        self.visual_time = 0.0
        self._shield_canvas = pygame.Surface((220, 220), pygame.SRCALPHA)
        self._shield_icon = load_power_up_icon(PowerUpType.SHIELD, 46)
        self._slow_overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
        )
        self._slow_overlay.fill((125, 205, 255, 25))
        pygame.draw.rect(
            self._slow_overlay, (180, 235, 255, 68),
            self._slow_overlay.get_rect(), width=8,
        )
        pygame.draw.rect(
            self._slow_overlay, (215, 245, 255, 30),
            self._slow_overlay.get_rect().inflate(-28, -28), width=3,
        )
        self._snow_canvas = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
        )
        rng = Random(42)
        self._snowflakes = [
            (
                rng.uniform(0, WINDOW_WIDTH),
                rng.uniform(0, WINDOW_HEIGHT),
                rng.uniform(35, 95),
                rng.uniform(-23, 23),
                rng.choice((1, 1, 2, 2, 3)),
                rng.uniform(0, tau),
            )
            for _ in range(72)
        ]

    def update(self, delta_time: float) -> None:
        """Actualiza las animaciones visuales del campo de batalla."""

        self.visual_time += max(0.0, delta_time)
        self.player_renderer.update(delta_time)
        self.enemy_renderer.update(delta_time)

    def register_player_keystroke(self) -> None:
        """Mantiene al jugador tecleando mientras recibe caracteres."""

        self.player_renderer.register_keystroke()

    def play_player_damage(self) -> None:
        """Activa la reacción visual a la pérdida de una vida."""

        self.player_renderer.play_damage()

    def play_enemy_summon(self, enemy: Enemy) -> None:
        """Muestra el conjuro al aparecer un esqueleto."""

        self.enemy_renderer.play_summon(enemy)

    def play_enemy_damage(self, enemy: Enemy) -> None:
        """Activa la reacción visual del enemigo que conserva vida."""

        self.enemy_renderer.play_damage(enemy)

    def play_enemy_death(self, enemy: Enemy) -> None:
        """Conserva visible la derrota después de retirar el objetivo."""

        self.enemy_renderer.play_death(enemy)

    def reset_enemy_animations(
        self, preserve_boss_death: bool = False
    ) -> None:
        """Descarta reacciones y permite acabar la muerte del golem."""

        self.enemy_renderer.reset(preserve_boss_death)

    def play_player_death(self) -> None:
        """Activa la animación final del jugador."""

        self.player_renderer.play_death()

    def play_player_revive(self) -> None:
        """Reproduce la secuencia inversa al comenzar de nuevo."""

        self.player_renderer.play_revive()

    def reset_player_animation(self) -> None:
        """Devuelve el jugador al idle al iniciar una partida normal."""

        self.player_renderer.reset()

    @property
    def is_player_death_finished(self) -> bool:
        """Indica cuándo puede mostrarse la pantalla de resultado."""

        return self.player_renderer.death_finished

    def draw(
        self,
        enemy_manager: EnemyManager,
        active_enemy: Enemy | None,
        typed_text: str,
        effect_manager: EffectManager,
        projectile_manager: ProjectileManager,
        power_up_manager: PowerUpManager,
    ) -> None:
        """Dibuja entidades, palabras y efectos sobre la arena."""

        self._draw_background()

        for enemy in enemy_manager.enemies:
            self.enemy_renderer.draw(self.screen, enemy)

        self.enemy_renderer.draw_defeats(self.screen)

        self.player_renderer.draw()
        self._draw_active_power_up_auras(power_up_manager)
        projectile_manager.draw(self.screen)

        # Los efectos quedan sobre las figuras y bajo las palabras legibles.
        effect_manager.draw(self.screen, self.small_font)
        self._draw_enemy_words(
            enemy_manager.enemies,
            active_enemy,
            typed_text,
        )

    def _draw_active_power_up_auras(
        self,
        power_up_manager: PowerUpManager,
    ) -> None:
        """Muestra estados preparados alrededor del jugador."""

        center = (round(PLAYER_POSITION[0]), round(PLAYER_POSITION[1]))
        if power_up_manager.shield_active:
            self._draw_shield_barrier((center[0], center[1] - 42))

    def _draw_shield_barrier(self, center: tuple[int, int]) -> None:
        """Forma un escudo dorado con borde de acero y reflejos cian."""

        canvas = self._shield_canvas
        canvas.fill((0, 0, 0, 0))
        pulse = 0.5 + 0.5 * sin(self.visual_time * 4.6)
        outline = (
            (110, 9), (179, 40), (195, 50), (189, 132),
            (169, 160), (110, 185), (51, 160), (31, 132),
            (25, 50), (41, 40),
        )
        pygame.draw.polygon(canvas, (255, 160, 44, 13 + round(8 * pulse)), outline)
        pygame.draw.lines(canvas, (9, 15, 35, 165), True, outline, width=12)
        pygame.draw.lines(canvas, (116, 133, 168, 158), True, outline, width=8)
        pygame.draw.lines(canvas, (245, 249, 255, 175), True, outline, width=3)
        pygame.draw.lines(
            canvas, (255, 174, 41, 176 + round(45 * pulse)), True,
            ((110, 21), (177, 52), (174, 127), (156, 149),
             (110, 170), (64, 149), (46, 127), (43, 52)), width=3,
        )
        pygame.draw.lines(
            canvas, (36, 225, 255, 225), False,
            outline[:5], width=4,
        )
        pygame.draw.lines(
            canvas, (255, 250, 225, 205), False,
            outline[6:] + outline[:1], width=3,
        )

        travel = self.visual_time * 4.0
        index = int(travel) % len(outline)
        fraction = travel % 1.0
        start = outline[index]
        finish = outline[(index + 1) % len(outline)]
        glint = (
            round(start[0] + (finish[0] - start[0]) * fraction),
            round(start[1] + (finish[1] - start[1]) * fraction),
        )
        pygame.draw.circle(canvas, (40, 205, 255, 90), glint, 12)
        pygame.draw.circle(canvas, (255, 255, 240, 235), glint, 4)

        if self._shield_icon is not None:
            self._shield_icon.set_alpha(round(185 + 55 * pulse))
            canvas.blit(self._shield_icon, self._shield_icon.get_rect(center=(110, 36)))
        self.screen.blit(canvas, (center[0] - 110, center[1] - 110))

    def draw_slow_overlay(self, power_up_manager: PowerUpManager) -> None:
        """Aplica escarcha tenue y copos animados a toda la pantalla."""

        if not power_up_manager.is_slow_active:
            return
        self.screen.blit(self._slow_overlay, (0, 0))
        self._snow_canvas.fill((0, 0, 0, 0))
        for x, y, speed, drift, radius, phase in self._snowflakes:
            snow_x = round((x + drift * self.visual_time
                            + 13 * sin(self.visual_time + phase)) % WINDOW_WIDTH)
            snow_y = round((y + speed * self.visual_time) % WINDOW_HEIGHT)
            pygame.draw.circle(
                self._snow_canvas, (235, 250, 255, 175),
                (snow_x, snow_y), radius,
            )
        self.screen.blit(self._snow_canvas, (0, 0))

    def draw_menu_background(self) -> None:
        """Dibuja únicamente el fondo limpio para las pantallas del menú."""

        self._draw_background()

    @staticmethod
    def _load_background(
        background_path: Path,
    ) -> pygame.Surface | None:
        """Carga el fondo optimizado y tolera recursos ausentes o dañados."""

        try:
            background = pygame.image.load(str(background_path)).convert()
        except (pygame.error, OSError):
            return None

        if background.get_size() != (WINDOW_WIDTH, WINDOW_HEIGHT):
            background = pygame.transform.smoothscale(
                background,
                (WINDOW_WIDTH, WINDOW_HEIGHT),
            )

        return background

    def _draw_background(self) -> None:
        """Dibuja la arena ilustrada o utiliza el color plano de respaldo."""

        if self.background is None:
            self.screen.fill(BACKGROUND_COLOR)
            return

        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.background_tint, (0, 0))

    def _draw_enemy_words(
        self,
        enemies: list[Enemy],
        active_enemy: Enemy | None,
        typed_text: str,
    ) -> None:
        """Dibuja la palabra y el estado de cada enemigo visible."""

        for enemy in enemies:
            self._draw_enemy_word(enemy, active_enemy, typed_text)

    def _draw_enemy_word(
        self,
        enemy: Enemy,
        active_enemy: Enemy | None,
        typed_text: str,
    ) -> None:
        """Dibuja una palabra y resalta el progreso del objetivo activo."""

        # La palabra completada desaparece mientras el proyectil viaja; el
        # enemigo sigue visible para recibir el impacto en pantalla.
        if enemy.is_pending_hit:
            return

        enemy_half_height = self.enemy_renderer.get_draw_height(enemy) // 2
        second_word = (
            getattr(enemy, "second_word", None)
            if enemy.enemy_type is EnemyType.ARMORED else None
        )
        word_center_y = max(
            135 if second_word else 105,
            round(enemy.position.y) - enemy_half_height - 12,
        )
        if second_word:
            word_center_y -= 30
        type_center_y = max(75, word_center_y - 30)

        # La recompensa base explica la diferencia entre palabras cortas y largas.
        base_points = round(
            len(enemy.word)
            * POINTS_PER_CHARACTER
            * enemy.score_multiplier
        )
        enemy_details = (
            f"{enemy.enemy_type.display_name}"
            f"  ·  {base_points} pts base"
        )

        if enemy.max_health > 1:
            shield_status = (
                f"Vida {enemy.health}/{enemy.max_health}"
                if enemy.enemy_type is EnemyType.BOSS
                else (
                    f"Escudo {enemy.health}/{enemy.max_health}"
                    if enemy.health == enemy.max_health
                    else "Armadura rota"
                )
            )
            enemy_details += f"  ·  {shield_status}"

        is_candidate = (
            enemy is active_enemy
            or (
                active_enemy is None
                and bool(typed_text)
                and enemy.word.startswith(typed_text)
            )
        )
        if is_candidate:
            enemy_details = f">  {enemy_details}"

        type_surface = self.small_font.render(
            enemy_details,
            True,
            enemy.label_color,
        )
        type_half_width = type_surface.get_width() // 2
        type_center_x = max(
            type_half_width + 20,
            min(
                round(enemy.position.x),
                WINDOW_WIDTH - type_half_width - 20,
            ),
        )
        type_rect = type_surface.get_rect(
            center=(
                type_center_x,
                type_center_y,
            )
        )
        self.screen.blit(type_surface, type_rect)

        if second_word:
            preview_surface = self.small_font.render(
                f"2ª: {second_word}", True, MUTED_TEXT_COLOR
            )
            preview_x = max(
                preview_surface.get_width() // 2 + 20,
                min(
                    round(enemy.position.x),
                    WINDOW_WIDTH - preview_surface.get_width() // 2 - 20,
                ),
            )
            self.screen.blit(
                preview_surface,
                preview_surface.get_rect(
                    center=(preview_x, word_center_y + 30)
                ),
            )

        character_surfaces = []

        # Solo el objetivo activo compara el texto introducido.
        for index, character in enumerate(enemy.word):
            if is_candidate and index < len(typed_text):
                character_color = (
                    CORRECT_COLOR
                    if typed_text[index] == character
                    else INCORRECT_COLOR
                )
            else:
                character_color = TEXT_COLOR

            character_surfaces.append(
                self.target_font.render(
                    character,
                    True,
                    character_color,
                )
            )

        total_width = sum(
            surface.get_width()
            for surface in character_surfaces
        )
        half_word_width = total_width // 2
        word_center_x = max(
            half_word_width + 20,
            min(
                round(enemy.position.x),
                WINDOW_WIDTH - half_word_width - 20,
            ),
        )
        character_x = word_center_x - half_word_width
        for character_surface in character_surfaces:
            character_rect = character_surface.get_rect(
                midleft=(character_x, word_center_y)
            )
            self.screen.blit(character_surface, character_rect)
            character_x += character_surface.get_width()
