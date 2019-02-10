from game_units.figures import Pawn, Queen, King, Knight, Rook, Bishop, Figure
from game_units.game_board import Board
from game_units.args_wrap import ArgsWrap
import os
import unittest

catalog = os.path.dirname(os.getcwd())
path = os.path.join(catalog, 'log', 'test.txt')
game = Board(ArgsWrap(path, "H-H", False, False))
white = "white"
black = "black"


class TestFigure(unittest.TestCase):
    def test_init(self):
        f = Figure("?", white, game)
        self.assertEqual(f.name, "?")
        self.assertEqual(f.color, white)

    def test_str(self):
        f = Figure("?", white, game)
        self.assertEqual(str(f), "?")

    def test_is_inside(self):
        self.assertTrue(Figure.is_inside(1, 1))
        self.assertTrue(Figure.is_inside(8, 8))
        self.assertFalse(Figure.is_inside(0, 0))
        self.assertFalse(Figure.is_inside(9, 9))

    def test_can_be_filled(self):
        f1 = Figure("", white, game)
        f2 = Figure("", white, game)
        f3 = Figure("", black, game)
        board = {(1, 1): f2, (4, 5): f3}
        self.assertTrue(f1.pos_can_be_placed(4, 5, board))
        self.assertTrue(f1.pos_can_be_placed(7, 7, board))
        self.assertFalse(f1.pos_can_be_placed(1, 1, board))


class TestFiguresClasses(unittest.TestCase):
    def test_queen(self):
        q = Queen("q", white, game)
        moves = q.possible_moves(1, 1, dict(), game)
        expected = {(x, y) for x in range(1, 9) for y in range(1, 9)
                    if (x, y) != (1, 1) and (x == 1 or y == 1 or x == y)}
        self.assertSetEqual(set(moves), expected)

    def test_king(self):
        q = King("k", white, game)
        moves = q.possible_moves(2, 2, dict(), game)
        expected = {(3, 2), (3, 3), (3, 1), (2, 3),
                    (2, 1), (1, 2), (1, 3), (1, 1), (8, 1)}
        self.assertSetEqual(set(moves), expected)

    def test_rook(self):
        q = Rook("r", white, game)
        x0, y0 = 4, 4
        moves = q.possible_moves(x0, y0, dict(), game)
        expected = {(x, y) for x in range(1, 9) for y in range(1, 9)
                    if (x == y0 or y == y0) and x != y}
        expected.add((5, 1))
        self.assertSetEqual(set(moves), expected)

    def test_knight(self):
        q = Knight("kn", white, game)
        moves = q.possible_moves(3, 3, dict(), game)
        expected = {(2, 1), (1, 2), (1, 4), (2, 5),
                    (4, 1), (4, 5), (5, 2), (5, 4)}
        self.assertSetEqual(set(moves), expected)

    def test_bishop(self):
        q = Bishop("b", white, game)
        moves = q.possible_moves(3, 3, dict(), game)
        expected = {(x, x) for x in range(1, 9) if x != 3}
        expected.update([(1, 5), (2, 4), (4, 2), (5, 1)])
        self.assertSetEqual(set(moves), expected)

    def test_pawn(self):
        q = Pawn("p", white, game)
        moves = q.possible_moves(2, 2, dict(), game)
        expected = {(2, 3), (2, 4)}
        self.assertSetEqual(set(moves), expected)


game.save_log()
#
# if __name__ == '__main__':
#     unittest.main()
