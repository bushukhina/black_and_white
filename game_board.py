from figures import Pawn, Queen, King, Knight, Rook, Bishop, Painter
import random
import sys
from GameState import GameState
from copy import deepcopy
from game_log_worker import GameLogWorker
white = "white"
black = "black"
turn = (white, black)
chars = {white: {Pawn: "♙", Rook: "♖", Knight: "♘", Bishop: "♗", King: "♔", Queen: "♕", Painter: "w"},
         black: {Pawn: "♟", Rook: "♜", Knight: "♞", Bishop: "♝", King: "♚", Queen: "♛", Painter: "b"}}


class Game:
    def __init__(self, args=None):
        self.use_painter = False
        self.save = False
        self.delete_log = False
        self.logger = None
        self.load_moves = []
        self.game_mode = {white: "'H", black: 'H'}
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
        self.impossible_check = False

        self.pawn_coord = None
        self.have_once_moved_pawn = False
        self.check = {white: False, black: False}
        self.pat = {white: False, black: False}
        self.mat = {white: False, black: False}

        self.was_three_repeats = False
        self.was_undo = False
        self.board_states = []
        self.board_states.append(deepcopy(self.board))
        self.board_states.append(deepcopy(self.board))

        self.painter_moved_partly = {white: None, black: None}
        self.move_painter = False
        self.painter_waiting = {white: None, black: None}

        self.game_states = []
        self.prev_state = {white: None, black: None}
        self.current_state = {white: self.get_state_dict(), black: self.get_state_dict()}
        self.game_states.append(self.get_state_dict())
        self.game_states.append(self.get_state_dict())
        self.next_state = {white: None, black: None}
        self.next_step = {white: None, black: None}
        self.is_checking_mat = False

    def play(self):
        while True:
            self.inform_check()
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
            if self.painter_moved_partly[self.player] is not None and \
                    self.painter_moved_partly[self.player][1] == start:
                moving_figure = self.board.get(self.painter_moved_partly[self.player][0], None)
            else:
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

        if type(moving_figure) == Painter:
            self.prepare_to_move_painter(moving_figure, start, end)
            if moving_figure.done_steps == 1:
                return
        elif self.painter_moved_partly[self.player] is not None:
            self.board[self.painter_moved_partly[self.player]].done_steps = 0

        if type(moving_figure) != Painter and self.painter_waiting[self.player] is not None:
            pos = self.painter_waiting[self.player]
            self.board[pos].wait_steps -= 1
            if self.board[pos].wait_steps == 0:
                self.painter_waiting[self.player] = None

        self.update_board(start, end)

        self.step += 1
        self.player = turn[self.step % 2]

        piece_dict = self.look_for_check()

        if self.impossible_check:
            self.undo_impossible_move()
            self.impossible_check = False
            if not self.is_checking_mat:
                print("King can't be left under check. Choose move to protect him")
            return

        if self.is_checking_mat:
            self.is_checking_mat = False
            self.undo_impossible_move()
            return

        if self.check[black]:
            self.look_for_mat(black, piece_dict)
        if self.check[white]:
            self.look_for_mat(white, piece_dict)

        self.check_pat()

        if not self.load_mode:
            if type(moving_figure) == Painter:
                prev_player = turn[(self.step - 1) % 2]
                self.logger.write(self.painter_moved_partly[prev_player][0], self.painter_moved_partly[prev_player][1])
                self.painter_moved_partly[prev_player] = None
            self.logger.write(start, end)
        self.save_step()
        if (not self.mat[white]) and (not self.mat[black]) and (not self.pat[white]) and (not self.pat[black]):
            self.check_board_state()
        if self.finish_the_game():
            self.save_log()
            print(self.game_state)
            sys.exit(0)

    def prepare_to_move_painter(self, moving_figure, start, end):
        if self.painter_moved_partly[self.player] is None:
            self.painter_moved_partly[self.player] = [start, end]
            moving_figure.done_steps = 1
        else:
            self.move_painter = True
            moving_figure.done_steps = 2

    def update_board(self, start, end):
        f1 = self.board.get(start, None)
        f2 = self.board.get(end, None)
        if self.move_painter:
            "Перекрашивание перепрыгнутой фигуры"
            painter_pos = self.painter_moved_partly[self.player][0]
            middle_field = Painter.get_medium_field(painter_pos, start)
            middle_figure = self.board.get(middle_field, None)
            if middle_figure is not None:
                figure_type = type(middle_figure)
                new_color = white if middle_figure.color == black else black
                self.board[middle_field].name = chars[new_color][figure_type]
                self.board[middle_field].color = new_color
            "Перемещение со сменой цвета painter'a"
            del self.board[painter_pos]
            another_player = turn[(self.step - 1) % 2]
            self.board[end] = Painter(chars[another_player][Painter], another_player, self)
            self.board[end].was_moved = True
            self.board[end].wait_steps = 2
            self.board[end].done_steps = 0
            self.painter_waiting[self.player] = end
            # эти координате необходимо сохранить для записи в лог
            # self.painter_moved_partly[self.player]
            self.move_painter = False
        elif f2 is not None and ((type(f1) is King and type(f2) is Rook) or (type(f2) is King and type(f1) is Rook)) \
                and self.move_is_castling(f1, f2, start, end):
            "рокировка"
            self.board[end], self.board[start] = self.board[start], self.board[end]
            self.board[end].was_moved = True
            self.board[start].was_moved = True
            self.board[end].castling = False
            self.board[start].castling = False
        else:
            "стандартный ход"
            self.board[end] = self.board[start]
            self.board[end].was_moved = True
            del self.board[start]
            self.board[end].castling = False

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
            "Удаление "
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

    def save_log(self):
        if self.delete_log:
            self.logger.delete_file()
            return
        if self.save:
            return
        answer = input('Want to save the game log? [y, n]')
        if answer == 'n':
            self.logger.delete_file()

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

    def get_state_dict(self):
        state = dict()
        state["pawn"] = self.have_once_moved_pawn
        state["pat"] = deepcopy(self.pat)
        state["painter"] = deepcopy(self.painter_waiting)
        state["check"] = deepcopy(self.check)
        state["mat"] = deepcopy(self.mat)
        state["pawn coord"] = deepcopy(self.pawn_coord)
        return state

    def update_state(self, state):
        self.have_once_moved_pawn = state["pawn"]
        self.mat = deepcopy(state["mat"])
        self.pat = deepcopy(state["pat"])
        self.painter_waiting = deepcopy(state["painter"])
        self.check = deepcopy(state["check"])
        self.pawn_coord = deepcopy(state["pawn coord"])

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
        self.is_checking_mode = False

    def look_for_check(self):
        self.is_checking_mode = True
        piece_dict = {black: [], white: []}
        for position, piece in self.board.items():
            if type(piece) == King:
                self.kings[piece.color] = position
            elif type(piece) == Painter:
                continue
            else:
                piece_dict[piece.color].append((piece, position))

        if self.can_see_king(self.kings[white], piece_dict[black]):
            if self.player == black:
                self.impossible_check = True
            self.check[white] = True
        else:
            self.check[white] = False

        if self.can_see_king(self.kings[black], piece_dict[white]):
            if self.player == white:
                """
                предотвращает шаг, после которого король останется под шахом и 
                шаг, когда ты сам ставишь короля под удар
                """
                self.impossible_check = True
            self.check[black] = True
        else:
            self.check[black] = False

        self.is_checking_mode = False
        return piece_dict

    def can_see_king(self, king_position, piece_list):
        for piece, piece_position in piece_list:
            if self.move_is_correct(piece, piece_position, king_position):
                return True
        return False

    def look_for_mat(self, color, figures):
        self.is_checking_mat = True
        king = self.kings[color]
        self.is_checking_mode = True

        if len(self.board.get(king).possible_moves(king[0], king[1], self.board, self)) > 0:
            "king can protect himself"
            self.mat[color] = False
            self.is_checking_mode = False
            self.is_checking_mat = False
            return
        self.is_checking_mode = False

        for figure, figure_pos in figures[color]:
            figure_moves = figure.possible_moves(figure_pos[0], figure_pos[1], self.board, self)
            for end in figure_moves:
                self.move(figure, figure_pos, end)
                if type(figure) != Painter:
                    if not self.is_checking_mat:
                        self.mat[color] = False
                        return
                else:
                    figure_moves1 = figure.possible_moves(end[0], end[1], self.board, self)
                    for end1 in figure_moves1:
                        self.move(figure, end, end1)
                        if not self.is_checking_mat:
                            self.mat[color] = False
                            return
        self.mat[color] = True
        self.is_checking_mat = False

    def move_is_correct(self, figure, start, end):
        return end in figure.possible_moves(start[0], start[1], self.board, self)

    def check_board_state(self):
        last_ind = len(self.game_states) - 1
        counter = 0
        prev = False
        if len(self.game_states) != len(self.board_states):
            print("some problem with state saving")
        for i in range(last_ind - 2, -1, -2):
            if prev:
                prev = False
                continue
            if Game.cmp_dicts(self.board_states[i], self.board_states[last_ind]) and \
                    self.game_states[i] == self.game_states[last_ind]:
                counter += 1
                prev = True
                if counter == 2:
                    self.was_three_repeats = True
                    break
            # print()

    @staticmethod
    def cmp_dicts(d1, d2):
        if d1.keys() != d2.keys():
            return False
        for key in d1.keys():
            if d1[key] != d2[key]:
                return False
        return True

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

    def unpack_args(self, parser):
        if parser is None:
            self.logger = GameLogWorker(None)
            self.delete_log = True
            return
        if parser.load:
            self.logger = GameLogWorker(parser.load)
            self.load_moves = self.logger.load()
        else:
            self.logger = GameLogWorker(None)
        mode = parser.mode.split('-')
        self.game_mode = {white: mode[0], black: mode[1]}
        self.endless_game = parser.endless
        self.use_painter = parser.painter
        self.save = parser.save

    def full_board(self):
        figures = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for x in range(1, 9):
            self.board[(x, 2)] = Pawn(chars[white][Pawn], white, self)
            self.board[(x, 7)] = Pawn(chars[black][Pawn], black, self)
            self.board[(x, 1)] = \
                figures[x - 1](chars[white][figures[x - 1]], white, self)
            self.board[(x, 8)] = \
                figures[x - 1](chars[black][figures[x - 1]], black, self)

        if self.use_painter:
            self.board[(8, 3)] = Painter('w', white, self)
            self.board[(1, 6)] = Painter('b', black, self)

    def __str__(self):
        if self.player == black and self.game_mode[black] == "H":
            f, t, d = 8, 0, -1
        else:
            f, t, d = 1, 9, 1
        s = "  " + "_" * 24
        result = "\n{} TURN\n".format(self.player.upper())
        for y in reversed(range(f, t, d)):
            result += s
            result += "\n"
            line = str(y) + "|"
            for x in range(f, t, d):
                if (x, y) in self.board:
                    line += " " + str(self.board[(x, y)]) + ""
                else:
                    line += " " + "▯" + ""
                line += "|"
            result += line
            result += "\n"
        result += s
        if self.player == black and self.game_mode[black] == "H":
            result += "\n   H  G  F  E  D  C  B  A"
        else:
            result += "\n   A  B  C  D  E  F  G  H"
        return result

    def finish_the_game(self):
        if self.game_state == GameState.notFinished:
            return False
        elif self.pat[white]:
            self.game_state = GameState.drawWhitePat
        elif self.pat[black]:
            self.game_state = GameState.drawBlackPat
        elif self.step == 85 and self.endless_game:
            self.game_state = GameState.drawStep85
        elif self.was_three_repeats:
            self.game_state = GameState.drawSameState3Times
        elif self.mat[white]:
            self.game_state = GameState.blackWin
        elif self.mat[black]:
            self.game_state = GameState.whiteWin
        return True

    def inform_check(self):
        if self.check[white]:
            print("White king is in check")
        elif self.check[black]:
            print("Black king is in check")
