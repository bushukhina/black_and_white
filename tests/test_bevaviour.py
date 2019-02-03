from game_units.figures import Knight, Painter
from game_units.game_board import Board
import os
import unittest

catalog = os.path.dirname(os.getcwd())
path = os.path.join(catalog, 'log', 'test.txt')

white = "white"
black = "black"


class ArgPiece:
    def __init__(self, file, p=False):
        self.load = os.path.join(catalog, 'log', file)
        self.mode = "H-H"
        self.endless = False
        self.painter = p


class TestBehaviour(unittest.TestCase):
    def test_check(self):
        ta = ArgPiece("black_check.txt")
        game = Board(ta, True)
        self.assertEqual(game.check[black], True)

    def test_simple_painter(self):
        ta = ArgPiece("painter_moves.txt", True)
        game = Board(ta, True)
        self.assertIsInstance(game.figures[8, 6], Painter)
        self.assertEqual(game.figures[8, 6].color, black)

    def test_painter_recolors(self):
        ta = ArgPiece("painter_recolors.txt", True)
        game = Board(ta, True)
        self.assertIsInstance(game.figures[3, 3], Painter)
        self.assertEqual(game.figures[3, 3].color, white)
        self.assertIsInstance(game.figures[2, 5], Knight)
        self.assertEqual(game.figures[2, 5].color, black)

    def test_draw_after_3_repeats(self):
        ta = ArgPiece("draw_three_repeats.txt")
        game = Board(ta, True)
        self.assertEqual(game.was_three_repeats, True)
