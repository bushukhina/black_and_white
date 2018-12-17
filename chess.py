# -*- coding: utf-8 -*-

import argparse
from game_board import Game


def parse_args():
    p = argparse.ArgumentParser(description="chess game")
    p.add_argument('--mode', help='Game mode(H-H, H-AI, AI-H, AI-AI)', nargs='?', default='H-H')
    p.add_argument('--endless', help='Do not stop after 85 steps', action='store_true')
    p.add_argument('--save',  '-s', help='Sage game log', default='store_true')
    p.add_argument('--load', '-l', help='File for game loading', nargs='?')
    p.add_argument('--figure1', help='Use extra figure1', action='store_true')
    # p.add_argument('--figure2', help='Use extra figure2',
    #                action='store_true')
    return p.parse_args()


parser = parse_args()
game = Game(parser)
game.play()
