from figures import Pawn, Queen, King, Knight, Rook, Bishop, Figure, Painter
from GameState import GameState
from game_board import Game

import unittest

white = "white"
black = "black"


class ArgPiece:
    def __init__(self, file, p=False):
        self.load = file
        self.mode = "H-H"
        self.endless = False
        self.painter = p
        self.save = False


class TestBehaviour(unittest.TestCase):
    def test_check(self):
        ta = ArgPiece(".\\log\\black_check.txt")
        game = Game(ta, True)
        game.play()
        self.assertEqual(game.check[black], True)

    def test_simple_painter(self):
        ta = ArgPiece(".\\log\\painter_moves.txt", True)
        game = Game(ta, True)
        game.play()
        # print([(k, str(f)) for k, f in game.board.items() if f.color == white])
        self.assertIsInstance(game.board[8, 6], Painter)
        self.assertEqual(game.board[8, 6].color, black)

    def test_painter_recolors(self):
        ta = ArgPiece(".\\log\\painter_recolors.txt", True)
        game = Game(ta, True)
        game.play()
        self.assertIsInstance(game.board[3, 3], Painter)
        self.assertEqual(game.board[3, 3].color, white)
        self.assertIsInstance(game.board[2, 5], Knight)
        self.assertEqual(game.board[2, 5].color, black)

    def test_draw_after_85_steps(self):
        ta = ArgPiece(".\\log\\draw_three_repeats.txt")
        game = Game(ta, True)
        game.play()
        self.assertEqual(game.game_state, GameState.drawSameState3Times)
