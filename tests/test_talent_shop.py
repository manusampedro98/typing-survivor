"""Regression checks for persistent purchases and their gameplay effects."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pygame

from game.armored_enemy import ArmoredEnemy
from game.enemy import Enemy
from game.game import Game
from game.game_state import GameState
from game.projectile_manager import EnergyHit
from game.save_manager import SaveManager
from game.settings import PLAYER_POSITION, MULTISHOT_CHAIN_TARGETS
from game.ui_renderer import MAIN_MENU_BUTTONS, SHOP_CARDS


class SaveManagerTalentTests(unittest.TestCase):
    def test_legacy_record_survives_points_and_purchases(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "save.json"
            path.write_text(json.dumps({"score": 96570, "wave": 11}), encoding="utf-8")
            save = SaveManager(path)
            self.assertEqual(save.available_points, 0)
            self.assertFalse(save.finish_run(5000, 3, 30, 90))
            self.assertTrue(save.purchase_talent("prepared_start"))
            self.assertEqual(save.available_points, 2000)
            self.assertFalse(save.purchase_talent("prepared_start"))
            self.assertFalse(save.purchase_talent("extra_life"))

            reloaded = SaveManager(path)
            self.assertEqual(reloaded.high_score.score, 96570)
            self.assertEqual(reloaded.available_points, 2000)
            self.assertEqual(reloaded.talent_level("prepared_start"), 1)

    def test_multilevel_limits_and_record_are_independent(self) -> None:
        with TemporaryDirectory() as directory:
            save = SaveManager(Path(directory) / "save.json")
            self.assertTrue(save.finish_run(200000, 8, 40, 95))
            for _ in range(3):
                self.assertTrue(save.purchase_talent("precision_pulse"))
            for _ in range(5):
                self.assertTrue(save.purchase_talent("multishot_plus"))
            self.assertFalse(save.purchase_talent("precision_pulse"))
            self.assertFalse(save.purchase_talent("multishot_plus"))
            self.assertEqual(save.high_score.score, 200000)
            self.assertEqual(SaveManager(save.save_file).talent_level("multishot_plus"), 5)


class GameTalentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = TemporaryDirectory()
        save = SaveManager(Path(self.directory.name) / "save.json")
        with patch("game.game.SaveManager", return_value=save):
            self.game = Game()

    def tearDown(self) -> None:
        pygame.quit()
        self.directory.cleanup()

    def test_shop_purchase_affects_next_run_and_banks_once(self) -> None:
        game = self.game
        game.save_manager.finish_run(30000, 5, 35, 90)
        game.state = GameState.MENU
        game._handle_mouse_click(MAIN_MENU_BUTTONS[1].center)
        self.assertIs(game.state, GameState.SHOP)
        game._handle_mouse_click(SHOP_CARDS[0].center)
        game._handle_mouse_click(SHOP_CARDS[1].center)
        self.assertEqual(game.save_manager.available_points, 7000)

        game._start_new_game()
        self.assertEqual(game.max_lives, 4)
        self.assertEqual(game.lives, 4)
        self.assertEqual(sum(game.power_up_manager.charges.values()), 1)
        game.score = 500
        game._finish_game()
        game._finish_game()
        self.assertEqual(game.save_manager.available_points, 7500)
        self.assertEqual(game.save_manager.high_score.score, 30000)

    def test_precision_requires_clean_word(self) -> None:
        game = self.game
        game.save_manager.finish_run(10000, 2, 30, 90)
        self.assertTrue(game.save_manager.purchase_talent("precision_pulse"))
        game._start_new_game()
        game.state = GameState.PLAYING
        game.enemy_manager.enemies = [Enemy("casa", (300, 200), PLAYER_POSITION)]
        game._append_text("casa")
        self.assertEqual(game.power_up_manager.precision_slow_time_remaining, 1.0)
        self.assertEqual(game.power_up_manager.enemy_speed_multiplier, 0.75)

        game._start_new_game()
        game.state = GameState.PLAYING
        game.enemy_manager.enemies = [Enemy("casa", (300, 200), PLAYER_POSITION)]
        game._append_text("cx")
        game._handle_control_key(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE)
        )
        game._append_text("asa")
        self.assertEqual(game.power_up_manager.precision_slow_time_remaining, 0.0)

    def test_combat_talents_affect_their_triggers(self) -> None:
        game = self.game
        game.save_manager.finish_run(100000, 7, 40, 90)
        for key in ("armor_break", "reactive_shield", "last_breath", "multishot_plus"):
            self.assertTrue(game.save_manager.purchase_talent(key))
        game.state = GameState.PLAYING

        armored = ArmoredEnemy("roca", (640, 380), PLAYER_POSITION)
        armored.second_word = "metal"
        armored.pending_hits = 1
        game.enemy_manager.enemies = [armored]
        before = armored.position.distance_to(PLAYER_POSITION)
        game._resolve_energy_hits([EnergyHit(armored, 0, armored.position.copy())])
        self.assertGreater(armored.position.distance_to(PLAYER_POSITION), before)

        reached = Enemy("fin", PLAYER_POSITION, PLAYER_POSITION)
        nearby = Enemy("sol", (PLAYER_POSITION[0], PLAYER_POSITION[1] - 100), PLAYER_POSITION)
        game.enemy_manager.enemies = [reached, nearby]
        game.power_up_manager.shield_active = True
        before = nearby.position.distance_to(PLAYER_POSITION)
        game._handle_enemy_arrivals()
        self.assertGreater(nearby.position.distance_to(PLAYER_POSITION), before)

        reached = Enemy("fin", PLAYER_POSITION, PLAYER_POSITION)
        simultaneous = Enemy("dos", PLAYER_POSITION, PLAYER_POSITION)
        game.enemy_manager.enemies = [reached, simultaneous]
        game.lives = 2
        game._handle_enemy_arrivals()
        self.assertEqual(game.lives, 1)
        self.assertTrue(game.last_breath_used)
        self.assertGreater(game.power_up_manager.emp_stun_time_remaining, 0)
        self.assertIsNot(game.state, GameState.DYING)

        target = Enemy("casa", (400, 250), PLAYER_POSITION)
        game.enemy_manager.enemies = [target]
        game.active_enemy = target
        game.power_up_manager.multishot_armed = True
        with patch.object(game.enemy_manager, "get_chain_targets", return_value=[]) as chain:
            game._complete_current_word()
            self.assertEqual(
                chain.call_args.kwargs["limit"], MULTISHOT_CHAIN_TARGETS + 1
            )


if __name__ == "__main__":
    unittest.main()
