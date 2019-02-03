import argparse
import sys
from game_units.args_wrap import ArgsWrap
from game_units.game_board import Board


def get_parser():
    p = argparse.ArgumentParser(description="chess game")
    p.add_argument('--mode', '-m', nargs='?', default='H-H',
                   help='Set game mode(H-H, H-AI, AI-H, AI-AI)', )
    p.add_argument('--endless', action='store_true',
                   help='Activate option not to stop after 85 steps')
    p.add_argument('-l', '--load', nargs='?', default=None,
                   help='Set file for game loading')
    p.add_argument('-p', '--painter', action='store_true',
                   help='Use optional figure Painter')
    return p.parse_args()


class ConsoleChess:
    def __init__(self, args):
        self.game = Board(ArgsWrap(args.load, args.mode,
                                   args.endless, args.painter))

    def close_log(self):
        self.game.save_log()

    def save_ask(self):
        answer = input('Want to save the game log? [y, n]')
        if answer == 'y':
            self.game.set_save()

    def end_game(self):
        self.save_ask()
        self.game.save_log()
        print("End of the game." + self.game.game_state)
        sys.exit(0)

    def play(self):
        while True:
            if self.game.finish_the_game():
                self.end_game()

            mess = self.game.inform_check()
            if mess:
                print(mess)
            print(self.game)

            start, end = self.game.get_coordinates()

            if start == "undo":
                self.game.undo()
                self.game.logger.write(start, end)
                continue

            if start == "redo":
                self.game.redo()
                self.game.logger.write(start, end)
                continue

            moving_figure = self.game.get_moving_figure(start)

            if moving_figure is not None:
                if self.game.move_is_correct(moving_figure, start, end):
                    if self.game.is_last_line(end):
                        f = self.game.get_figure_type()
                        self.game.set_figure_type(f)
                    self.game.move(moving_figure, start, end)
                else:
                    print("Move is not possible")
            else:
                print("Your figure on given position not found")


parser = get_parser()
con_game = ConsoleChess(parser)
con_game.play()
