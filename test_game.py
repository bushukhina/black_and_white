import unittest
from game_board import Game
from figures import Pawn, Queen, King, Knight, Rook, Bishop
white = "white"
black = "black"


class TestGame(unittest.TestCase):
    def test_init(self):
        game = Game()
        self.assertEqual(game.step, 0)
        self.assertEqual(game.player, white)
        self.assertIsInstance(game.board, dict)
        for y in [1, 2, 7, 8]:
            for x in range(1, 9):
                self.assertIn((x, y), game.board)

        for x in range(1, 9):
            self.assertIsInstance(game.board[(x, 2)], Pawn)
            self.assertEqual(game.board[(x, 2)].color, white)

        for x in range(1, 9):
            self.assertIsInstance(game.board[(x, 7)], Pawn)
            self.assertEqual(game.board[(x, 7)].color, black)

        figures = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for x in range(1, 9):
            self.assertIsInstance(game.board[(x, 1)], figures[x-1])
            self.assertEqual(game.board[(x, 1)].color, white)

        for x in range(1, 9):
            self.assertIsInstance(game.board[(x, 8)], figures[x-1])
            self.assertEqual(game.board[(x, 8)].color, black)

    def test_move_is_correct(self):
        g = Game()
        self.assertTrue(g.move_is_correct(g.board[(1, 2)], (1, 2), (1, 4)))
        self.assertTrue(g.move_is_correct(g.board[(7, 1)], (7, 1), (6, 3)))

    def test_convert_positions(self):
        self.assertEqual(Game.convert_positions("h2", "h3"), ((8, 2), (8, 3)))

    def test_str(self):
        expected = """
WHITE TURN
_______________________________
8| ♜| ♞| ♝| ♛| ♚| ♝| ♞| ♜|
_______________________________
7| ♟| ♟| ♟| ♟| ♟| ♟| ♟| ♟|
_______________________________
6| ▯| ▯| ▯| ▯| ▯| ▯| ▯| ▯|
_______________________________
5| ▯| ▯| ▯| ▯| ▯| ▯| ▯| ▯|
_______________________________
4| ▯| ▯| ▯| ▯| ▯| ▯| ▯| ▯|
_______________________________
3| ▯| ▯| ▯| ▯| ▯| ▯| ▯| ▯|
_______________________________
2| ♙| ♙| ♙| ♙| ♙| ♙| ♙| ♙|
_______________________________
1| ♖| ♘| ♗| ♕| ♔| ♗| ♘| ♖|
_______________________________
  A   B   C   D   E   F   G   H"""
        game = Game()
        self.assertEqual(str(game), expected)


if __name__ == '__main__':
    unittest.main()