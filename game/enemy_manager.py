"""Creación y gestión de los enemigos presentes en pantalla."""

from random import choice, choices, uniform

import pygame

from game.armored_enemy import ArmoredEnemy
from game.enemy_type import EnemyType
from game.boss_enemy import BossEnemy
from game.enemy import Enemy
from game.fast_enemy import FastEnemy
from game.goblin_enemy import GoblinEnemy
from game.necromancer_enemy import NecromancerEnemy
from game.skeleton_enemy import SkeletonEnemy
from game.settings import (
    ARMORED_ENEMY_FIRST_WAVE,
    FAST_ENEMY_FIRST_WAVE,
    GOBLIN_ENEMY_FIRST_WAVE,
    ENEMY_SPAWN_MIN_SEPARATION,
    ENEMY_SPAWN_PATH_POINTS,
    ENEMY_SPAWN_POSITION_ATTEMPTS,
    ENEMY_SPAWN_VERTICAL_JITTER,
    NECROMANCER_MAX_SKELETONS,
    NECROMANCER_ENEMY_FIRST_WAVE,
    NECROMANCER_SUMMON_OFFSETS,
    PLAYER_POSITION,
    WINDOW_WIDTH,
)
from game.wave_manager import WaveManager
from game.word_manager import WordManager


class EnemyManager:
    """Gestiona aparición, movimiento y selección de enemigos."""

    def __init__(
        self,
        word_manager: WordManager,
        wave_manager: WaveManager,
    ) -> None:
        """Guarda las dependencias y prepara una colección vacía."""

        self.word_manager = word_manager
        self.wave_manager = wave_manager
        self.enemies: list[Enemy] = []
        self.spawn_elapsed = 0.0

    def reset(self) -> None:
        """Prepara el primer enemigo de una partida nueva."""

        self.enemies.clear()
        self.spawn_elapsed = 0.0
        self.start_wave()

    def clear_for_wave_break(self) -> None:
        """Retira objetivos y detiene el cronómetro de apariciones."""
        self.enemies.clear()
        self.spawn_elapsed = 0.0

    def start_wave(self) -> None:
        """Genera el único jefe o el primer rival de la oleada normal."""
        self.spawn_elapsed = 0.0
        if self.wave_manager.is_boss_wave:
            self.spawn_enemy(BossEnemy)
        else:
            self.spawn_enemy()

    def update(
        self,
        delta_time: float,
        movement_multiplier: float = 1.0,
    ) -> list[Enemy]:
        """Mueve los enemigos y genera refuerzos cuando corresponde."""

        for enemy in tuple(self.enemies):
            # El multiplicador afecta al movimiento, no al ritmo de aparición.
            enemy.update(delta_time * max(0.0, movement_multiplier))

        summoners: list[Enemy] = []
        if movement_multiplier > 0.0:
            summoners.extend(self._summon_skeletons())
            summoners.extend(self._summon_boss_minions())
        self.spawn_elapsed = min(
            self.spawn_elapsed + delta_time,
            self.wave_manager.enemy_spawn_interval,
        )

        if (
            not self.wave_manager.is_boss_wave
            and self.spawn_elapsed >= self.wave_manager.enemy_spawn_interval
            and len(self.enemies)
            < self.wave_manager.max_simultaneous_enemies
        ):
            self.spawn_enemy()
            self.spawn_elapsed = 0.0

        return summoners

    def spawn_enemy(
        self,
        enemy_class: type[Enemy] | None = None,
    ) -> Enemy:
        """Crea un enemigo en una posición aleatoria de la franja trasera."""

        enemy_class = enemy_class or self._choose_enemy_class()
        enemy_type = {
            Enemy: EnemyType.NORMAL,
            GoblinEnemy: EnemyType.GOBLIN,
            FastEnemy: EnemyType.FAST,
            ArmoredEnemy: EnemyType.ARMORED,
            NecromancerEnemy: EnemyType.NECROMANCER,
            SkeletonEnemy: EnemyType.SKELETON,
            BossEnemy: EnemyType.BOSS,
        }[enemy_class]
        start_position = self._get_random_start_position()
        used_words = self._active_words()
        word = self.word_manager.choose_for_enemy(
            enemy_type, self.wave_manager.current_wave, used_words
        )

        enemy_kwargs = dict(
            word=word,
            start_position=start_position,
            target_position=PLAYER_POSITION,
            speed=self._get_balanced_speed(start_position),
        )
        if enemy_class is BossEnemy:
            enemy_kwargs["wave_number"] = self.wave_manager.current_wave
        enemy = enemy_class(**enemy_kwargs)
        if enemy_class is ArmoredEnemy:
            enemy.second_word = self.word_manager.choose_for_enemy(
                EnemyType.ARMORED,
                self.wave_manager.current_wave,
                used_words | {word},
            )
        self.enemies.append(enemy)
        return enemy

    def remove(self, enemy: Enemy) -> None:
        """Retira un enemigo si todavía pertenece a la colección."""

        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def ensure_enemy(self) -> None:
        """Evita que la partida quede sin ningún objetivo disponible."""

        if self.wave_manager.is_boss_wave:
            if not self.enemies:
                self.spawn_enemy(BossEnemy)
                self.spawn_elapsed = 0.0
            return
        if not any(not enemy.is_pending_hit for enemy in self.enemies):
            self.spawn_enemy()
            self.spawn_elapsed = 0.0

    def replace_word(self, enemy: Enemy) -> None:
        """Asigna una palabra nueva a un enemigo que sigue con vida."""

        if isinstance(enemy, ArmoredEnemy) and not isinstance(enemy, BossEnemy):
            if enemy.second_word is not None:
                enemy.word = enemy.second_word
                enemy.second_word = None
                enemy.second_word_exposed = True
                return
        enemy.word = self.word_manager.choose_for_enemy(
            enemy.enemy_type,
            self.wave_manager.current_wave,
            self._active_words(excluded_enemy=enemy),
        )

    def matching_targets(self, prefix: str) -> list[Enemy]:
        """Devuelve todos los objetivos que aceptan el prefijo escrito."""
        return [
            enemy for enemy in self.enemies
            if not enemy.is_pending_hit and enemy.word.startswith(prefix)
        ]

    def select_target(self, prefix: str) -> Enemy | None:
        """Escoge un objetivo de respaldo si el prefijo deja de ser válido."""
        candidates = self.matching_targets(prefix)
        if not candidates:
            return None
        return min(
            candidates,
            key=lambda enemy: enemy.position.distance_to(
                enemy.target_position
            ),
        )

    def send_all_to_start(self) -> None:
        """Devuelve a cada enemigo a su punto exacto de aparición."""

        for enemy in self.enemies:
            enemy.reset_to_start()

    def get_chain_targets(
        self,
        excluded_enemy: Enemy,
        limit: int,
    ) -> list[Enemy]:
        """Elige los enemigos más cercanos para un impacto encadenado."""

        candidates = [
            enemy
            for enemy in self.enemies
            if (
                enemy is not excluded_enemy
                and not enemy.is_pending_hit
                and enemy.pending_hits == 0
            )
        ]
        candidates.sort(
            key=lambda enemy: enemy.position.distance_to(
                enemy.target_position
            )
        )
        return candidates[:max(0, limit)]

    def reached_enemies(self) -> list[Enemy]:
        """Devuelve los enemigos que han alcanzado la base."""

        return [
            enemy
            for enemy in self.enemies
            if enemy.has_reached_target()
        ]

    def _summon_skeletons(self) -> list[NecromancerEnemy]:
        """Invoca sin sobrepasar los límites globales ni los de cada mago."""
        summoners = []
        for necromancer in tuple(self.enemies):
            if not isinstance(necromancer, NecromancerEnemy):
                continue
            if necromancer.is_pending_hit or not necromancer.ready_to_summon:
                continue
            if (
                not self.wave_manager.is_boss_wave
                and len(self.enemies) >= self.wave_manager.max_simultaneous_enemies
            ):
                break

            active_skeletons = sum(
                isinstance(enemy, SkeletonEnemy)
                and enemy.summoner is necromancer
                for enemy in self.enemies
            )
            if active_skeletons >= NECROMANCER_MAX_SKELETONS:
                continue

            offset = NECROMANCER_SUMMON_OFFSETS[
                necromancer.summons_made % len(NECROMANCER_SUMMON_OFFSETS)
            ]
            spawn_position = (
                max(70.0, min(WINDOW_WIDTH - 70.0, necromancer.position.x + offset[0])),
                min(PLAYER_POSITION[1] - 50.0, necromancer.position.y + offset[1]),
            )
            skeleton = SkeletonEnemy(
                word=self.word_manager.choose_for_enemy(
                    EnemyType.SKELETON,
                    self.wave_manager.current_wave,
                    self._active_words(),
                ),
                start_position=spawn_position,
                target_position=PLAYER_POSITION,
                speed=self._get_balanced_speed(spawn_position),
                summoner=necromancer,
            )
            self.enemies.append(skeleton)
            necromancer.mark_summoned()
            summoners.append(necromancer)

        return summoners

    def _summon_boss_minions(self) -> list[BossEnemy]:
        """Cada 1,5 segundos añade un rival de los tipos desbloqueados."""
        if not self.wave_manager.is_boss_wave:
            return []
        boss = next(
            (enemy for enemy in self.enemies if isinstance(enemy, BossEnemy)),
            None,
        )
        if boss is None or boss.is_pending_hit or not boss.ready_to_summon:
            return []
        available_classes: list[type[Enemy]] = [Enemy, GoblinEnemy]
        if self.wave_manager.current_wave >= ARMORED_ENEMY_FIRST_WAVE:
            available_classes.append(ArmoredEnemy)
        if self.wave_manager.current_wave >= FAST_ENEMY_FIRST_WAVE:
            available_classes.append(FastEnemy)
        # El nigromante se adelanta una ronda solo para el jefe de la 10.
        if self.wave_manager.current_wave >= 10:
            available_classes.append(NecromancerEnemy)
        enemy_class = choice(available_classes)
        self.spawn_enemy(enemy_class)
        boss.mark_summoned()
        return [boss]

    def _choose_enemy_class(self) -> type[Enemy]:
        """Selecciona una clase según las probabilidades de la oleada."""

        wave = self.wave_manager.current_wave
        classes: list[type[Enemy]] = [Enemy]
        weights = [4]
        if wave >= GOBLIN_ENEMY_FIRST_WAVE:
            classes.append(GoblinEnemy)
            weights.append(4)
        if wave >= ARMORED_ENEMY_FIRST_WAVE:
            classes.append(ArmoredEnemy)
            weights.append(2)
        if wave >= FAST_ENEMY_FIRST_WAVE:
            classes.append(FastEnemy)
            weights.append(2)
        if wave >= NECROMANCER_ENEMY_FIRST_WAVE:
            classes.append(NecromancerEnemy)
            weights.append(1)
        return choices(classes, weights=weights, k=1)[0]

    def _get_random_start_position(self) -> tuple[float, float]:
        """Elige una posición aleatoria sobre la franja trasera de la plaza."""

        if not self.enemies:
            return self._create_spawn_candidate()

        best_candidate = self._create_spawn_candidate()
        best_clearance = 0.0

        for _ in range(ENEMY_SPAWN_POSITION_ATTEMPTS):
            candidate = self._create_spawn_candidate()
            candidate_vector = pygame.Vector2(candidate)
            clearance = min(
                candidate_vector.distance_to(enemy.position)
                for enemy in self.enemies
            )
            if clearance >= ENEMY_SPAWN_MIN_SEPARATION:
                return candidate
            if clearance > best_clearance:
                best_candidate = candidate
                best_clearance = clearance

        return best_candidate

    @staticmethod
    def _create_spawn_candidate() -> tuple[float, float]:
        """Interpola un punto de la curva trasera con una variación leve."""

        spawn_x = uniform(
            ENEMY_SPAWN_PATH_POINTS[0][0],
            ENEMY_SPAWN_PATH_POINTS[-1][0],
        )
        spawn_y = ENEMY_SPAWN_PATH_POINTS[-1][1]

        for start_point, end_point in zip(
            ENEMY_SPAWN_PATH_POINTS,
            ENEMY_SPAWN_PATH_POINTS[1:],
        ):
            if spawn_x > end_point[0]:
                continue

            segment_width = end_point[0] - start_point[0]
            progress = (
                0.0
                if segment_width == 0.0
                else (spawn_x - start_point[0]) / segment_width
            )
            spawn_y = start_point[1] + (
                end_point[1] - start_point[1]
            ) * progress
            break

        spawn_y += uniform(
            -ENEMY_SPAWN_VERTICAL_JITTER,
            ENEMY_SPAWN_VERTICAL_JITTER,
        )
        return (spawn_x, spawn_y)

    def _get_balanced_speed(
        self,
        start_position: tuple[float, float],
    ) -> float:
        """Compensa la distancia para mantener estable el tiempo de llegada."""

        reference_start = ENEMY_SPAWN_PATH_POINTS[
            len(ENEMY_SPAWN_PATH_POINTS) // 2
        ]
        reference_distance = pygame.Vector2(reference_start).distance_to(
            PLAYER_POSITION
        )
        spawn_distance = pygame.Vector2(start_position).distance_to(
            PLAYER_POSITION
        )
        return (
            self.wave_manager.enemy_speed
            * spawn_distance
            / reference_distance
        )

    def _active_words(
        self,
        excluded_enemy: Enemy | None = None,
    ) -> set[str]:
        """Reúne las palabras usadas por los demás enemigos."""

        words = set()
        for enemy in self.enemies:
            if enemy is excluded_enemy:
                continue
            words.add(enemy.word)
            if isinstance(enemy, ArmoredEnemy) and enemy.second_word:
                words.add(enemy.second_word)
        return words
