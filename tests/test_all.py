import unittest
from tests.test_game import TestGame
from tests.test_figures import TestFigure, TestFiguresClasses
from tests.test_bevaviour import TestBehaviour


def make_suite():
    suite = unittest.TestSuite()
    for test in (TestFigure, TestFiguresClasses, TestGame, TestBehaviour):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite


if __name__ == '__main__':
    unittest.main()
