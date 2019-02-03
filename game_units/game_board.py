from game_units.figures import Pawn, Queen, King, Knight, Rook, Bishop, Painter
from game_units.game_state import GameState
from game_units.game_log_worker import GameLogWorker
import random
from copy import deepcopy

WHITE = "white"
BLACK = "black"
turn = (WHITE, BLACK)
chars = {WHITE: {Pawn: "♙", Rook: "♖", Knight: "♘",
                 Bishop: "♗", King: "♔", Queen: "♕", Painter: "w"},
         BLACK: {Pawn: "♟", Rook: "♜", Knight: "♞",
                 Bishop: "♝", King: "♚", Queen: "♛", Painter: "b"}}


class Board:
    def __init__(self, args=None):
        self.use_painter = False
        self.delete_log = False
        self.save = False
        self.logger = None
        self.load_moves = []
        self.game_mode = {WHITE: "'H", BLACK: 'H'}
        self.endless_game = False
        self.unpack_args(args)
        self.load_mode = False

        self.direction = {WHITE: 1, BLACK: -1}
        self.figures = {}
        self.full_board()
        self.step = 0
        self.player = turn[0]
        self.game_state = GameState.NOT_FINISHED

        self.kings = {WHITE: (-1, -1), BLACK: (-1, -1)}
        self.is_checking_mode = False
        self.pawn_last_line = {WHITE: 8, BLACK: 1}
        self.impossible_check = False

        self.pawn_coord = None
        self.have_once_moved_pawn = False
        self.check = {WHITE: False, BLACK: False}
        self.pat = {WHITE: False, BLACK: False}
        self.mat = {WHITE: False, BLACK: False}

        self.was_three_repeats = False
        self.was_undo = False
        self.board_states = []
        self.board_states.append(deepcopy(self.figures))
        self.board_states.append(deepcopy(self.figures))

        self.painter_moved_partly = {WHITE: None, BLACK: None}
        self.move_painter = False
        self.painter_waiting = {WHITE: None, BLACK: None}

        self.game_states = []
        self.prev_state = {WHITE: None, BLACK: None}
        self.current_state = \
            {WHITE: self.get_state_dict(), BLACK: self.get_state_dict()}
        self.game_states.append(self.get_state_dict())
        self.game_states.append(self.get_state_dict())
        self.next_state = {WHITE: None, BLACK: None}
        self.next_step = {WHITE: None, BLACK: None}
        self.is_checking_mat = False
        self.load_log()

    def get_moving_figure(self, start):
        if self.painter_moved_partly[self.player] is not None and \
                self.painter_moved_partly[self.player][1] == start:
            moving_figure = self.figures.get(
                self.painter_moved_partly[self.player][0], None)
        else:
            moving_figure = self.figures.get(start, None)

        if moving_figure is None or moving_figure.color != self.player:
            return None
        return moving_figure

    def load_log(self):
        self.load_mode = True
        while len(self.load_moves) > 0:
            start, end = self.load_moves.pop()
            f = self.get_moving_figure(start)
            self.move(f, start, end)
        self.load_mode = False

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
            self.figures[self.painter_moved_partly[self.player]].done_steps = 0

        if type(moving_figure) != Painter and \
                self.painter_waiting[self.player] is not None:
            pos = self.painter_waiting[self.player]
            self.figures[pos].wait_steps -= 1
            if self.figures[pos].wait_steps == 0:
                self.painter_waiting[self.player] = None

        self.update_board(start, end)

        self.step += 1
        self.player = turn[self.step % 2]

        piece_dict = self.look_for_check()

        if self.impossible_check:
            self.undo_impossible_move()
            self.impossible_check = False
            if not self.is_checking_mat:
                # print("King can't be left under check. "
                #       "Choose move to protect him")
                return

        if self.is_checking_mat:
            self.is_checking_mat = False
            self.undo_impossible_move()
            return

        if self.check[BLACK]:
            self.look_for_mat(BLACK, piece_dict)
        if self.check[WHITE]:
            self.look_for_mat(WHITE, piece_dict)

        self.check_pat()

        if not self.load_mode:
            if type(moving_figure) == Painter:
                prev_player = turn[(self.step - 1) % 2]
                self.logger.write(self.painter_moved_partly[prev_player][0],
                                  self.painter_moved_partly[prev_player][1])
                self.painter_moved_partly[prev_player] = None
            self.logger.write(start, end)
        self.save_step()

        if (not self.mat[WHITE]) and (not self.mat[BLACK]) \
                and (not self.pat[WHITE]) and (not self.pat[BLACK]):
            self.check_board_state()

    def prepare_to_move_painter(self, moving_figure, start, end):
        if self.painter_moved_partly[self.player] is None:
            self.painter_moved_partly[self.player] = [start, end]
            moving_figure.done_steps = 1
            # print("done 1 step")
        else:
            self.move_painter = True
            moving_figure.done_steps = 2

    def update_board(self, start, end):
        f1 = self.figures.get(start, None)
        f2 = self.figures.get(end, None)
        if self.move_painter:
            # Перекрашивание перепрыгнутой фигуры
            painter_pos = self.painter_moved_partly[self.player][0]
            middle_field = Painter.get_medium_field(painter_pos, start)
            middle_figure = self.figures.get(middle_field, None)
            if middle_figure is not None:
                figure_type = type(middle_figure)
                new_color = WHITE if middle_figure.color == BLACK else BLACK
                self.figures[middle_field].name = chars[new_color][figure_type]
                self.figures[middle_field].color = new_color
            # Перемещение со сменой цвета painter'a
            del self.figures[painter_pos]
            another_player = turn[(self.step - 1) % 2]
            self.figures[end] = \
                Painter(chars[another_player][Painter], another_player, self)
            self.figures[end].was_moved = True
            self.figures[end].wait_steps = 2
            self.figures[end].done_steps = 0
            self.painter_waiting[self.player] = end
            self.move_painter = False
        elif f2 is not None and \
                ((type(f1) is King and type(f2) is Rook) or
                 (type(f2) is King and type(f1) is Rook)) \
                and self.move_is_castling(f1, f2, start, end):
            # "рокировка"
            self.figures[end], self.figures[start] = \
                self.figures[start], self.figures[end]
            self.figures[end].was_moved = True
            self.figures[start].was_moved = True
            self.figures[end].castling = False
            self.figures[start].castling = False
        else:
            # "стандартный ход"
            self.figures[end] = self.figures[start]
            self.figures[end].was_moved = True
            del self.figures[start]
            self.figures[end].castling = False

    def move_is_castling(self, f1, f2, start, end):
        if not f1.castling and not f2.catling:
            return False
        if self.player == WHITE:
            return (start == (5, 1) and end in [(1, 1), (8, 1)]) or \
                    (end == (5, 1) and start in [(1, 1), (8, 1)])
        else:
            return (start == (5, 8) and end in [(8, 8), (1, 8)]) or \
                    (end == (5, 8) and start in [(8, 8), (1, 8)])

    def prepare_to_move_pawn(self, moving_figure, start, end):
        if self.have_once_moved_pawn:
            # "Удаление "
            if moving_figure.en_passant:
                moving_figure.en_passant = False
                pawn_attacked = self.pawn_coord[1]
                if pawn_attacked[0] == end[0]:
                    del self.figures[pawn_attacked]
            self.have_once_moved_pawn = False
            self.pawn_coord = None

        if not moving_figure.was_moved:
            # Сохраняются данные, чтобы проверить,
            # возможно ли след ходом взятие на проходе
            self.pawn_coord = [start, end]
            self.have_once_moved_pawn = True

        if end[1] == self.pawn_last_line[self.player]:
            # Превращение пешки
            new_type = self.get_figure()
            if new_type is not None:
                self.figures[start] = \
                    new_type(chars[self.player][new_type], self.player, self)

    def save_step(self):
        self.board_states.append(deepcopy(self.figures))
        self.prev_state[self.player] = \
            deepcopy(self.current_state[self.player])
        self.current_state[self.player] = self.get_state_dict()
        self.game_states.append(self.get_state_dict())

        if self.was_undo:
            self.next_state[WHITE] = self.next_step[WHITE] = None
            self.next_state[BLACK] = self.next_step[BLACK] = None
            self.was_undo = False

    def undo_impossible_move(self):
        self.step -= 1
        self.player = turn[self.step % 2]
        self.update_state(self.current_state[self.player])
        self.figures = deepcopy(self.board_states[len(self.board_states) - 1])

    def undo(self):
        another_player = turn[(self.step + 1) % 2]

        if self.prev_state[self.player] is None or \
                self.prev_state[another_player] is None:
            return

        self.step -= 2

        self.game_states = self.game_states[:-2]
        self.next_step[self.player] = deepcopy(self.board_states.pop())
        self.next_step[another_player] = deepcopy(self.board_states.pop())
        self.figures = deepcopy(self.board_states[len(self.board_states) - 1])

        self.next_state[self.player] = \
            deepcopy(self.current_state[self.player])
        self.next_state[another_player] = \
            deepcopy(self.current_state[another_player])

        self.update_state(self.prev_state[self.player])
        self.current_state[self.player] = self.get_state_dict()
        self.current_state[another_player] = \
            deepcopy(self.prev_state[another_player])

        self.prev_state[WHITE] = self.prev_state[BLACK] = None
        self.was_undo = True
        if not self.load_mode:
            self.logger.write("undo", None)

    def redo(self):
        another_player = turn[(self.step + 1) % 2]

        if self.next_step[self.player] is None or \
                self.next_state[self.player] is None or \
                self.next_step[another_player] is None or \
                self.next_state[another_player] is None:
            return

        self.step += 2
        self.game_states.append(deepcopy(self.next_state[another_player]))
        self.game_states.append(deepcopy(self.next_state[self.player]))

        self.board_states.append(deepcopy(self.next_step[another_player]))
        self.board_states.append(deepcopy(self.next_step[self.player]))
        self.figures = deepcopy(self.board_states[len(self.board_states) - 1])

        self.prev_state[self.player] = \
            deepcopy(self.current_state[self.player])
        self.prev_state[another_player] = \
            deepcopy(self.current_state[another_player])

        self.current_state[another_player] = \
            deepcopy(self.next_state[another_player])
        self.update_state(self.next_state[self.player])
        self.current_state[self.player] = self.get_state_dict()

        self.next_step[WHITE] = self.next_state[WHITE] = None
        self.next_step[BLACK] = self.next_state[BLACK] = None
        if not self.load_mode:
            self.logger.write("redo", None)

    def get_state_dict(self):
        return {"pawn": self.have_once_moved_pawn,
                "pat": deepcopy(self.pat),
                "painter": deepcopy(self.painter_waiting),
                "check": deepcopy(self.check),
                "mat": deepcopy(self.mat),
                "pawn coord": deepcopy(self.pawn_coord)}

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
        for position, piece in self.figures.items():
            if self.player == piece.color:
                if len(piece.possible_moves(position[0], position[1],
                                            self.figures, self)) > 0:
                    self.is_checking_mode = False
                    return
        self.pat[self.player] = True
        self.is_checking_mode = False

    def look_for_check(self):
        self.is_checking_mode = True
        piece_dict = {BLACK: [], WHITE: []}
        for position, piece in self.figures.items():
            if type(piece) == King:
                self.kings[piece.color] = position
            elif type(piece) == Painter:
                continue
            else:
                piece_dict[piece.color].append((piece, position))

        if self.can_see_king(self.kings[WHITE], piece_dict[BLACK]):
            if self.player == BLACK:
                self.impossible_check = True
            self.check[WHITE] = True
        else:
            self.check[WHITE] = False

        if self.can_see_king(self.kings[BLACK], piece_dict[WHITE]):
            if self.player == WHITE:
                # """
                # предотвращает шаг, после которого король останется под шахом,
                # шаг, когда ты сам ставишь короля под удар
                # """
                self.impossible_check = True
            self.check[BLACK] = True
        else:
            self.check[BLACK] = False

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

        if len(self.figures.get(king).possible_moves(king[0], king[1],
                                                     self.figures, self)) > 0:
            # "king can protect himself"
            self.mat[color] = False
            self.is_checking_mode = False
            self.is_checking_mat = False
            return
        self.is_checking_mode = False

        for figure, figure_pos in figures[color]:
            figure_moves = figure.possible_moves(figure_pos[0], figure_pos[1],
                                                 self.figures, self)
            for end in figure_moves:
                self.move(figure, figure_pos, end)
                if type(figure) != Painter:
                    if not self.is_checking_mat:
                        self.mat[color] = False
                        return
                else:
                    figure_moves1 = figure.possible_moves(end[0], end[1],
                                                          self.figures, self)
                    for end1 in figure_moves1:
                        self.move(figure, end, end1)
                        if not self.is_checking_mat:
                            self.mat[color] = False
                            return
        self.mat[color] = True
        self.is_checking_mat = False

    def move_is_correct(self, figure, start, end):
        return end in figure.possible_moves(start[0], start[1],
                                            self.figures, self)

    def check_board_state(self):
        last_ind = len(self.game_states) - 1
        counter = 0
        prev = False
        for i in range(last_ind - 2, -1, -2):
            if prev:
                prev = False
                continue
            if self.game_states[i] == self.game_states[last_ind] and \
                    Board.cmp_dicts(self.board_states[i],
                                    self.board_states[last_ind]):
                counter += 1
                prev = True
                if counter == 2:
                    self.was_three_repeats = True
                    break

    def unpack_args(self, parser):
        if parser is None:
            self.logger = GameLogWorker(None)
            self.delete_log = True
            return

        if parser.load is not None:
            self.save = True
            self.logger = GameLogWorker(parser.load)
            self.load_moves = self.logger.load()
        else:
            self.logger = GameLogWorker(None)

        mode = parser.mode.split('-')
        self.game_mode = {WHITE: mode[0], BLACK: mode[1]}
        self.endless_game = parser.endless
        self.use_painter = parser.painter

    def finish_the_game(self):
        if self.pat[WHITE]:
            self.game_state = GameState.DRAW_WHITE_PAT
        elif self.pat[BLACK]:
            self.game_state = GameState.DRAW_BLACK_PAT
        elif self.step == 85 and self.endless_game:
            self.game_state = GameState.DRAW_85_STEPS
        elif self.was_three_repeats:
            self.game_state = GameState.DRAW_REPEAT_STATE
        elif self.mat[WHITE]:
            self.game_state = GameState.BLACK_WIN
        elif self.mat[BLACK]:
            self.game_state = GameState.WHITE_WIN

        if self.game_state == GameState.NOT_FINISHED:
            return False
        return True

    @staticmethod
    def cmp_dicts(d1, d2):
        if d1.keys() != d2.keys():
            return False
        for key in d1.keys():
            if d1[key] != d2[key]:
                return False
        return True

    def get_ai_move(self):
        state = (-1, -1)
        moves = []
        for pos, piece in self.figures.items():
            if piece.color == self.player:
                moves = \
                    piece.possible_moves(pos[0], pos[1], self.figures, self)
                if len(moves) > 0:
                    state = pos
                    break
        if state == (-1, -1):
            return (-1, -1), (-1, -1)
        return state, random.choice(moves)

    def full_board(self):
        classes = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for x in range(1, 9):
            self.figures[(x, 2)] = Pawn(chars[WHITE][Pawn], WHITE, self)
            self.figures[(x, 7)] = Pawn(chars[BLACK][Pawn], BLACK, self)
            self.figures[(x, 1)] = \
                classes[x - 1](chars[WHITE][classes[x - 1]], WHITE, self)
            self.figures[(x, 8)] = \
                classes[x - 1](chars[BLACK][classes[x - 1]], BLACK, self)

        if self.use_painter:
            self.figures[(8, 3)] = Painter('w', WHITE, self)
            self.figures[(1, 6)] = Painter('b', BLACK, self)

    def save_log(self):
        if self.delete_log or not self.save:
            self.logger.delete_file()

    def set_save(self):
        self.save = True

    @staticmethod
    def get_figure():
        print("Now you can make your pawn to be queen, knight, rook or bishop")
        print("Input q for queen, b for bishop, k for knight or r for rook")
        in_value = input("pawn will become: ")
        d = {"q": Queen, "b": Bishop, "k": Knight, "r": Rook}
        figure = d.get(in_value, None)
        return figure

    def inform_check(self):
        if self.check[WHITE]:
            return "White king is in check"
        elif self.check[BLACK]:
            return "Black king is in check"
        return ""

    def is_ai_move(self):
        return self.game_mode[self.player] == "AI"

    def bot_make_move(self):
        move = self.get_ai_move()
        f = self.get_moving_figure(move[0])
        self.move(f, move[0], move[1])
