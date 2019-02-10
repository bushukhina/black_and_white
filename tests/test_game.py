import unittest
import os
from game_units.game_board import Board
from game_units.args_wrap import ArgsWrap
from game_units.figures import Pawn, Queen, King, Knight, Rook, Bishop
white = "white"
black = "black"

catalog = os.path.dirname(os.getcwd())
path = os.path.join(catalog, 'log', 'test.txt')


class TestGame(unittest.TestCase):
    def test_init(self):
        game = Board(ArgsWrap(path, "H-H", False, False))
        self.assertEqual(game.step, 0)
        self.assertEqual(game.player, white)
        self.assertIsInstance(game.figures, dict)
        for y in [1, 2, 7, 8]:
            for x in range(1, 9):
                self.assertIn((x, y), game.figures)

        for x in range(1, 9):
            self.assertIsInstance(game.figures[(x, 2)], Pawn)
            self.assertEqual(game.figures[(x, 2)].color, white)

        for x in range(1, 9):
            self.assertIsInstance(game.figures[(x, 7)], Pawn)
            self.assertEqual(game.figures[(x, 7)].color, black)

        figures = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for x in range(1, 9):
            self.assertIsInstance(game.figures[(x, 1)], figures[x-1])
            self.assertEqual(game.figures[(x, 1)].color, white)

        for x in range(1, 9):
            self.assertIsInstance(game.figures[(x, 8)], figures[x-1])
            self.assertEqual(game.figures[(x, 8)].color, black)

    def test_move_is_correct(self):
        game = Board(ArgsWrap(path, "H-H", False, False))
        self.assertTrue(game.move_is_correct(
            game.figures[(1, 2)], (1, 2), (1, 4)))
        self.assertTrue(game.move_is_correct(
            game.figures[(7, 1)], (7, 1), (6, 3)))

    def test_convert_positions(self):
        self.assertEqual(Board.convert_positions("h2", "h3"), ((8, 2), (8, 3)))

# if __name__ == '__main__':
#     unittest.main()
