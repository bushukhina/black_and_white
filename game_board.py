# -*- coding: utf-8 -*-

from figures import Pawn, Queen, King, Knight, Rook, Bishop
import random
import sys
from GameState import GameState
from copy import deepcopy
from game_log_worker import GameLogWorker
white = "white"
black = "black"
turn = (white, black)
chars = {white: {Pawn: "♙", Rook: "♖", Knight: "♘", Bishop: "♗", King: "♔", Queen: "♕"},
         black: {Pawn: "♟", Rook: "♜", Knight: "♞", Bishop: "♝", King: "♚", Queen: "♛"}}


class Game:
    def __init__(self, args):
        self.save = False
        self.logger = None
        self.load_moves = []
        self.game_mode = {white: None, black: None}
        self.endless_game = False
        self.unpack_args(args)
        self.load_mode = False

        self.direction = {white: 1, black: -1}
        self.board = {}
        self.full_board()
        self.step = 0
        self.player = turn[0]
        self.game_state = GameState.notFinished

        self.kings = {white: (-1, -1), black: (-1, -1)}
        self.is_checking_mode = False
        self.pawn_last_line = {white: 8, black: 1}
        self.double_check = False

        self.pawn_coord = None
        self.have_once_moved_pawn = False
        self.check = {white: False, black: False}
        self.pat = {white: False, black: False}

        self.was_three_repeats = False
        self.was_undo = False
        self.board_states = []
        self.board_states.append(deepcopy(self.board))
        self.board_states.append(deepcopy(self.board))

        self.game_states = []
        self.prev_state = {white: None, black: None}
        self.current_state = {white: self.get_state_dict(), black: self.get_state_dict()}
        self.game_states.append(self.get_state_dict())
        self.game_states.append(self.get_state_dict())
        self.next_state = {white: None, black: None}
        self.next_step = {white: None, black: None}

    def play(self):
        while True:
            print(self)
            if len(self.load_moves) > 0:
                self.load_mode = True
                start, end = self.load_moves.pop()
            else:
                self.load_mode = False
                start, end = self.get_coordinates()
            if start == "undo":
                self.undo()
                if not self.load_mode:
                    self.logger.write(start, end)
                continue
            if start == "redo":
                self.redo()
                if not self.load_mode:
                    self.logger.write(start, end)
                continue
            moving_figure = self.board.get(start, None)
            if moving_figure is not None:
                if moving_figure.color != self.player:
                    print("It is not your figure!")
                    continue
                if self.move_is_correct(moving_figure, start, end):
                    self.move(moving_figure, start, end)
                else:
                    print("Move is not possible")
            else:
                print("No figure on given position found")

    def move(self, moving_figure, start, end):
        if type(moving_figure) == Pawn:
            self.prepare_to_move_pawn(moving_figure, start, end)
        else:
            self.have_once_moved_pawn = False
            self.pawn_coord = None

        self.update_board(start, end)

        self.step += 1
        self.player = turn[self.step % 2]

        self.look_for_check()
        if self.double_check:
            self.undo_impossible_move()
            self.double_check = False
            print("King can't be left under check. Choose move to protect him")
            return

        self.check_pat()
        self.save_step()
        if not self.load_mode:
            self.logger.write(start, end)
        self.check_board_state()
        if self.finish_the_game():
            self.save_log()
            print(self.game_state)
            sys.exit(0)

    def save_log(self):
        if self.save:
            return
        answer = input('Want to save the game log? [y, n]')
        if answer == 'n':
            self.logger.delete_file()

    def check_board_state(self):
        last_ind = len(self.game_states) - 1
        counter = 0
        prev = False
        if len(self.game_states) != len(self.board_states):
            print("we have a problem")
        for i in range(last_ind - 2, -1, -2):
            if prev:
                prev = False
                continue
            if self.board_states[i] == self.board_states[last_ind] and \
                    self.game_states[i] == self.game_states[last_ind]:
                counter += 1
                prev = True
                if counter == 2:
                    self.was_three_repeats = True
                    break
            print()

    @staticmethod
    def cmp_dicts(d1, d2):
        if d1.keys() != d2.keys():
            return False
        for key in d1.keys():
            if d1[key] != d2[key]:
                return False
        return True

    def unpack_args(self, parser):
        self.save = parser.save
        # print(parser.load)
        if parser.load:
            self.logger = GameLogWorker(parser.load)
            self.load_moves = self.logger.load()
        else:
            self.logger = GameLogWorker(None)
        mode = parser.mode.split('-')
        self.game_mode = {white: mode[0], black: mode[1]}
        self.endless_game = parser.endless

    def save_step(self):
        self.board_states.append(deepcopy(self.board))
        self.prev_state[self.player] = deepcopy(self.current_state[self.player])
        self.current_state[self.player] = self.get_state_dict()
        self.game_states.append(self.get_state_dict())

        if self.was_undo:
            self.next_state[white] = self.next_step[white] = None
            self.next_state[black] = self.next_step[black] = None
            self.was_undo = False

    def undo_impossible_move(self):
        self.step -= 1
        self.player = turn[self.step % 2]
        self.update_state(self.current_state[self.player])
        self.board = deepcopy(self.board_states[len(self.board_states) - 1])

    def undo(self):
        self.step -= 2
        another_player = turn[(self.step + 1) % 2]

        if self.prev_state[self.player] is None or self.prev_state[another_player] is None:
            print("impossible to undo")
            return

        self.game_states = self.game_states[:-2]
        self.next_step[self.player] = deepcopy(self.board_states.pop())
        self.next_step[another_player] = deepcopy(self.board_states.pop())
        self.board = deepcopy(self.board_states[len(self.board_states) - 1])

        self.next_state[self.player] = deepcopy(self.current_state[self.player])
        self.next_state[another_player] = deepcopy(self.current_state[another_player])

        self.update_state(self.prev_state[self.player])
        self.current_state[self.player] = self.get_state_dict()
        self.current_state[another_player] = deepcopy(self.prev_state[another_player])

        self.prev_state[white] = self.prev_state[black] = None
        self.was_undo = True

    def redo(self):
        self.step += 2
        another_player = turn[(self.step + 1) % 2]

        if self.next_step[self.player] is None or self.next_state[self.player] is None or \
                self.next_step[another_player] is None or self.next_state[another_player] is None:
            print("impossible to undo")
            return

        self.game_states.append(deepcopy(self.next_state[another_player]))
        self.game_states.append(deepcopy(self.next_state[self.player]))

        self.board_states.append(deepcopy(self.next_step[another_player]))
        self.board_states.append(deepcopy(self.next_step[self.player]))
        self.board = deepcopy(self.board_states[len(self.board_states) - 1])

        self.prev_state[self.player] = deepcopy(self.current_state[self.player])
        self.prev_state[another_player] = deepcopy(self.current_state[another_player])

        self.current_state[another_player] = deepcopy(self.next_state[another_player])
        self.update_state(self.next_state[self.player])
        self.current_state[self.player] = self.get_state_dict()

        self.next_step[white] = self.next_state[white] = None
        self.next_step[black] = self.next_state[black] = None

    def update_board(self, start, end):
        f1 = self.board.get(start, None)
        f2 = self.board.get(end, None)

        if f2 is not None and ((type(f1) is King and type(f2) is Rook) or (type(f2) is King and type(f1) is Rook)) \
                and self.move_is_castling(f1, f2, start, end):
            self.board[end], self.board[start] = self.board[start], self.board[end]
            self.board[end].was_moved = True
            self.board[start].was_moved = True
            self.board[end].castling = False
            self.board[start].castling = False
        else:
            self.board[end] = self.board[start]
            self.board[end].was_moved = True
            del self.board[start]
            self.board[end].castling = False

    def get_state_dict(self):
        state = dict()
        state["pawn"] = self.have_once_moved_pawn
        state["pat"] = deepcopy(self.pat)
        state["check"] = deepcopy(self.check)
        state["pawn coord"] = deepcopy(self.pawn_coord)
        return state

    def update_state(self, state):
        self.have_once_moved_pawn = state["pawn"]
        # self.is_castling = state["castling"]
        self.pat = deepcopy(state["pat"])
        self.check = deepcopy(state["check"])
        self.pawn_coord = deepcopy(state["pawn coord"])

    def move_is_castling(self, f1, f2, start, end):
        if not f1.castling and not f2.catling:
            return False
        if self.player == white:
            if start == (5, 1) and (end == (1, 1) or end == (8, 1)):
                return True
            elif end == (5, 1) and (start == (1, 1) or start == (8, 1)):
                return True
            else:
                return False
        if self.player == black:
            if start == (5, 8) and (end == (1, 8) or end == (8, 8)):
                return True
            elif end == (5, 8) and (start == (1, 8) or start == (8, 8)):
                return True
            else:
                return False

    def prepare_to_move_pawn(self, moving_figure, start, end):
        if self.have_once_moved_pawn:
            if moving_figure.en_passant:
                moving_figure.en_passant = False
                pawn_attacked = self.pawn_coord[1]
                if pawn_attacked[0] == end[0]:
                    del self.board[pawn_attacked]
            self.have_once_moved_pawn = False
            self.pawn_coord = None

        if not moving_figure.was_moved:
            "Сохраняются данные, чтобы проверить, возможно ли след ходом взятие на проходе"
            self.pawn_coord = [start, end]
            self.have_once_moved_pawn = True

        if end[1] == self.pawn_last_line[self.player]:
            "Превращение пешки"
            new_type = self.get_figure()
            if new_type is not None:
                self.board[start] = new_type(chars[self.player][new_type], self.player, self)

    def finish_the_game(self):
        if self.pat[white] or self.pat[black] or \
                (self.step == 85 and self.endless_game) or self.was_three_repeats:
            self.game_state = GameState.draw
            return True
        return False

    def check_pat(self):
        if self.check[self.player]:
            return
        self.is_checking_mode = True
        for position, piece in self.board.items():
            if self.player == piece.color:
                if len(piece.possible_moves(position[0], position[1], self.board, self)) > 0:
                    self.is_checking_mode = False
                    return
        self.pat[self.player] = True
        print('pat' + self.player)
        self.is_checking_mode = False

    def look_for_check(self):
        self.is_checking_mode = True
        piece_dict = {black: [], white: []}
        for position, piece in self.board.items():
            if type(piece) == King:
                self.kings[piece.color] = position
            else:
                piece_dict[piece.color].append((piece, position))

        if self.can_see_king(self.kings[white], piece_dict[black]):
            print("White player is in check")
            if self.check[white]:
                self.double_check = True
            self.check[white] = True
        else:
            self.check[white] = False

        if self.can_see_king(self.kings[black], piece_dict[white]):
            print("Black player is in check.")
            if self.check[black]:
                self.double_check = True
            self.check[black] = True
        else:
            self.check[black] = False

        self.is_checking_mode = False

    def can_see_king(self, king_position, piece_list):
        for piece, piece_position in piece_list:
            if self.move_is_correct(piece, piece_position, king_position):
                return True
        return False

    def get_ai_move(self):
        state = (-1, -1)
        moves = []
        for pos, piece in self.board.items():
            if piece.color == self.player:
                moves = piece.possible_moves(pos[0], pos[1], self.board, self)
                if len(moves) > 0:
                    state = pos
                    break
        if state == (-1, -1):
            return (-1, -1), (-1, -1)
        n = random.randint(0, len(moves) - 1)
        return state, moves[n]

    def move_is_correct(self, figure, start, end):
        return end in figure.possible_moves(start[0], start[1], self.board, self)

    @staticmethod
    def get_figure():
        print("Now you can make your pawn to be queen, knight, rook or bishop")
        print("Input q for queen, b for bishop, k for knight or r for rook")
        in_value = input("pawn will become: ")
        d = {"q": Queen, "b": Bishop, "k": Knight, "r": Rook}
        figure = d.get(in_value, None)
        return figure

    def get_coordinates(self):
        if self.game_mode[self.player] == "H":
            start, end = self.parse_input()
        else:
            start, end = self.get_ai_move()
        return start, end

    @staticmethod
    def parse_input():
        a = input("from: ")
        b = input("to: ")
        if a == "undo" or a == "redo":
            return a, None
        return Game.convert_positions(a, b)

    @staticmethod
    def convert_positions(a, b):
        try:
            a = (ord(a[0]) - 96), int(a[1])
            b = (ord(b[0]) - 96), int(b[1])
            return a, b
        except ValueError:
            print("Incorrect input.")
            return (-1, -1), (-1, -1)
        except IndexError:
            print("Incorrect input.")
            return (-1, -1), (-1, -1)

    def full_board(self):
        figures = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for x in range(1, 9):
            self.board[(x, 2)] = Pawn(chars[white][Pawn], white, self)
            self.board[(x, 7)] = Pawn(chars[black][Pawn], black, self)
            self.board[(x, 1)] = \
                figures[x - 1](chars[white][figures[x - 1]], white, self)
            self.board[(x, 8)] = \
                figures[x - 1](chars[black][figures[x - 1]], black, self)

    def __str__(self):
        s = "_" * 31
        result = "\n{} TURN\n".format(self.player.upper())
        for y in reversed(range(1, 9)):
            result += s
            result += "\n"
            line = str(y) + "|"
            for x in range(1, 9):
                if (x, y) in self.board:
                    line += " " + str(self.board[(x, y)]) + ""
                else:
                    line += " " + "▯" + ""
                line += "|"
# ▯
            result += line
            result += "\n"
        result += s
        result += "\n  A   B   C   D   E   F   G   H"
        return result
