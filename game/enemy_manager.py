"""Creación y gestión de los enemigos presentes en pantalla."""

from random import random

from game.armored_enemy import ArmoredEnemy
from game.enemy import Enemy
from game.fast_enemy import FastEnemy
from game.settings import (
    ENEMY_LANE_START_POSITIONS,
    PLAYER_POSITION,
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
        self.next_lane_index = 0

    def reset(self, preserve_first_enemy: bool = False) -> None:
        """Prepara el primer enemigo de una partida nueva."""

        if preserve_first_enemy and len(self.enemies) == 1:
            # El enemigo del menú ya ocupa el carril central y no se ha movido.
            self.spawn_elapsed = 0.0
            self.next_lane_index = 1
            return

        self.enemies.clear()
        self.spawn_elapsed = 0.0
        self.next_lane_index = 0
        self.spawn_enemy()

    def update(self, delta_time: float) -> None:
        """Mueve los enemigos y genera refuerzos cuando corresponde."""

        for enemy in self.enemies:
            enemy.update(delta_time)

        self.spawn_elapsed = min(
            self.spawn_elapsed + delta_time,
            self.wave_manager.enemy_spawn_interval,
        )

        if (
            self.spawn_elapsed >= self.wave_manager.enemy_spawn_interval
            and len(self.enemies)
            < self.wave_manager.max_simultaneous_enemies
        ):
            self.spawn_enemy()
            self.spawn_elapsed = 0.0

    def spawn_enemy(self) -> Enemy:
        """Crea un enemigo usando un carril y una palabra disponibles."""

        enemy_class = self._choose_enemy_class()
        start_position = self._get_next_start_position()
        word = self.word_manager.choose_word(self._active_words())

        enemy = enemy_class(
            word=word,
            start_position=start_position,
            target_position=PLAYER_POSITION,
            speed=self.wave_manager.enemy_speed,
        )
        self.enemies.append(enemy)
        return enemy

    def remove(self, enemy: Enemy) -> None:
        """Retira un enemigo si todavía pertenece a la colección."""

        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def ensure_enemy(self) -> None:
        """Evita que la partida quede sin ningún objetivo disponible."""

        if not self.enemies:
            self.spawn_enemy()
            self.spawn_elapsed = 0.0

    def replace_word(self, enemy: Enemy) -> None:
        """Asigna una palabra nueva a un enemigo que sigue con vida."""

        enemy.word = self.word_manager.choose_word(
            self._active_words(excluded_enemy=enemy)
        )

    def select_target(self, first_character: str) -> Enemy | None:
        """Elige el enemigo más cercano cuya palabra empiece por la letra."""

        candidates = [
            enemy
            for enemy in self.enemies
            if enemy.word.startswith(first_character)
        ]

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda enemy: enemy.position.distance_to(
                enemy.target_position
            ),
        )

    def reached_enemies(self) -> list[Enemy]:
        """Devuelve los enemigos que han alcanzado la base."""

        return [
            enemy
            for enemy in self.enemies
            if enemy.has_reached_target()
        ]

    def _choose_enemy_class(self) -> type[Enemy]:
        """Selecciona una clase según las probabilidades de la oleada."""

        enemy_roll = random()
        armored_limit = self.wave_manager.armored_enemy_chance
        fast_limit = armored_limit + self.wave_manager.fast_enemy_chance

        if enemy_roll < armored_limit:
            return ArmoredEnemy
        if enemy_roll < fast_limit:
            return FastEnemy
        return Enemy

    def _get_next_start_position(self) -> tuple[float, float]:
        """Rota los carriles para repartir los enemigos verticalmente."""

        start_position = ENEMY_LANE_START_POSITIONS[self.next_lane_index]
        self.next_lane_index = (
            self.next_lane_index + 1
        ) % len(ENEMY_LANE_START_POSITIONS)
        return start_position

    def _active_words(
        self,
        excluded_enemy: Enemy | None = None,
    ) -> set[str]:
        """Reúne las palabras usadas por los demás enemigos."""

        return {
            enemy.word
            for enemy in self.enemies
            if enemy is not excluded_enemy
        }
