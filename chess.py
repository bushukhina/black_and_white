import argparse
from game_board import Game


def get_parser():
    p = argparse.ArgumentParser(description="chess game")
    p.add_argument('--mode', help='Game mode(H-H, H-AI, AI-H, AI-AI)', nargs='?', default='H-H')
    p.add_argument('--endless', help='Do not stop after 85 steps', action='store_true')
    p.add_argument('--load', '-l', help='File for game loading', nargs='?', default=None)
    p.add_argument('--figure1', help='Use extra figure1', action='store_true')
    # p.add_argument('--figure2', help='Use extra figure2',
    #                action='store_true')
    return p.parse_args()


parser = get_parser()
game = Game(parser)
game.play()
