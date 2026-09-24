"""Checks for the game-over menu and its return paths."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pygame

from game.game import Game
from game.game_state import GameState
from game.save_manager import SaveManager
from game.ui_renderer import GAME_OVER_ACTIONS, GAME_OVER_BUTTONS, OPTIONS_CLOSE_BUTTON


class GameOverMenuTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = TemporaryDirectory()
        save = SaveManager(Path(self.directory.name) / "save.json")
        with patch("game.game.SaveManager", return_value=save):
            self.game = Game()
        self.game.state = GameState.GAME_OVER

    def tearDown(self) -> None:
        pygame.quit()
        self.directory.cleanup()

    def test_mouse_actions_return_to_game_over(self) -> None:
        game = self.game
        self.assertEqual(
            GAME_OVER_ACTIONS,
            ("REINICIAR", "TIENDA", "AYUDA", "OPCIONES", "SALIR"),
        )

        game._handle_mouse_motion(GAME_OVER_BUTTONS[1].center)
        self.assertEqual(game.game_over_selection, 1)
        game._handle_mouse_click(GAME_OVER_BUTTONS[1].center)
        self.assertIs(game.state, GameState.SHOP)
        game._handle_control_key(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertIs(game.state, GameState.GAME_OVER)

        game._handle_mouse_click(GAME_OVER_BUTTONS[2].center)
        self.assertIs(game.state, GameState.HELP)
        game._activate_help_action("CERRAR")
        self.assertIs(game.state, GameState.GAME_OVER)

        game._handle_mouse_click(GAME_OVER_BUTTONS[3].center)
        self.assertIs(game.state, GameState.OPTIONS)
        game._handle_mouse_click(OPTIONS_CLOSE_BUTTON.center)
        self.assertIs(game.state, GameState.GAME_OVER)

        game._handle_mouse_click(GAME_OVER_BUTTONS[0].center)
        self.assertIs(game.state, GameState.COUNTDOWN)

    def test_keyboard_navigation_and_exit(self) -> None:
        game = self.game
        game._handle_control_key(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
        self.assertEqual(game.game_over_selection, 4)
        game._handle_control_key(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        self.assertFalse(game.running)


if __name__ == "__main__":
    unittest.main()
