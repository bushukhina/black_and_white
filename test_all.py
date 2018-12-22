import unittest
from test_game import TestGame
from test_figures import TestFigure, TestFiguresClasses
from test_bevaviour import TestBehaviour


def make_suite():
    suite = unittest.TestSuite()
    for test in (TestFigure, TestFiguresClasses, TestGame, TestBehaviour):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite


if __name__ == '__main__':
    unittest.main()
