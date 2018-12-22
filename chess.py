import argparse
from game_board import Game


def get_parser():
    p = argparse.ArgumentParser(description="chess game")
    p.add_argument('--mode', '-m', help='Set game mode(H-H, H-AI, AI-H, AI-AI)', nargs='?', default='H-H')
    p.add_argument('--endless', help='Activate option not to stop after 85 steps', action='store_true')
    p.add_argument('-s', '--save', help='Save game log', action='store_true')
    p.add_argument('-l', '--load', help='Set file for game loading', nargs='?', default=None)
    p.add_argument('-p', '--painter',  help='Use optional figure Painter(to get more information use README.md)',
                   action='store_true')
    return p.parse_args()


parser = get_parser()
game = Game(parser)
game.play()
