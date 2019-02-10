class Figure:
    def __init__(self, name, color, game, moved=False):
        self.name = name
        self.color = color
        self.game = game
        self.was_moved = moved

    def possible_moves(self, x0, y0, board, game):
        pass

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.name, self.color, self.was_moved) == \
               (other.name, other.color, other.was_moved)

    @staticmethod
    def is_inside(x, y):
        return 1 <= x <= 8 and 1 <= y <= 8

    def pos_can_be_placed(self, x, y, board):
        return Figure.is_inside(x, y) and \
               ((x, y) not in board or board[(x, y)].color != self.color)

    def generate_moves(self, x0, y0, board, deltas):
        ends = []
        for dx, dy in deltas:
            x, y = x0 + dx, y0 + dy
            while self.is_inside(x, y):
                target = board.get((x, y), None)
                if target is None:
                    ends.append((x, y))
                elif target.color != self.color:
                    ends.append((x, y))
                    break
                else:
                    break
                x, y = x + dx, y + dy
        return ends


straights = [(1, 0), (0, 1), (-1, 0), (0, -1)]
diagonals = [(1, 1), (-1, 1), (1, -1), (-1, -1)]


class Queen(Figure):
    def possible_moves(self, x0, y0, board, game):
        return self.generate_moves(x0, y0, board, deltas=straights + diagonals)


class King(Figure):
    def __init__(self, name, color, game):
        super().__init__(name, color, game)
        self.castling = False

    def __eq__(self, other):
        return super().__eq__(other) and self.castling == other.castling

    def possible_moves(self, x0, y0, board, game):
        moves = [(x, y) for x, y in King.get_permutations(x0, y0)
                 if self.pos_can_be_placed(x, y, board)
                 and not self.move_creates_check((x, y), game)]
        if not self.was_moved:
            moves += [(x, y) for x, y in self.get_castling_moves(game)
                      if not self.move_creates_check((x, y), game)]
        return moves

    def get_castling_moves(self, game):
        moves = []
        if not self.was_moved:
            if self.color == "white":
                moves += self.check_rook_pos((1, 1), game)
                moves += self.check_rook_pos((8, 1), game)
            else:
                moves += self.check_rook_pos((1, 8), game)
                moves += self.check_rook_pos((8, 8), game)
        if len(moves) > 0 and not game.is_checking_mode:
            self.castling = True
        return moves

    @staticmethod
    def check_rook_pos(pos, game):
        rk = game.figures.get(pos, None)
        if rk is not None:
            if not rk.was_moved:
                return [pos]
        return []

    def move_creates_check(self, k_pos, game):
        for position, piece in self.game.figures.items():
            if self.color != piece.color:
                if type(piece) == Painter:
                    continue
                if type(piece) == King:
                    if k_pos in \
                            piece.get_permutations(position[0], position[1]):
                        return True
                elif type(piece) == Pawn:
                    if k_pos in \
                            piece.get_check_moves(position[0], position[1]):
                        return True
                elif k_pos in piece.possible_moves(position[0], position[1],
                                                   self.game.figures, game):
                    return True
        return False

    @staticmethod
    def get_permutations(x, y):
        return [(x + 1, y), (x + 1, y + 1), (x + 1, y - 1), (x, y + 1),
                (x, y - 1), (x - 1, y), (x - 1, y + 1), (x - 1, y - 1)]


class Knight(Figure):
    def possible_moves(self, x0, y0, board, game):
        return [(x, y) for x, y in Knight.get_permutations(x0, y0)
                if self.pos_can_be_placed(x, y, board)]

    @staticmethod
    def get_permutations(x, y):
        return [(x + 1, y + 2), (x - 1, y + 2), (x + 1, y - 2), (x - 1, y - 2),
                (x + 2, y + 1), (x - 2, y + 1), (x + 2, y - 1), (x - 2, y - 1)]


class Bishop(Figure):
    def possible_moves(self, x0, y0, board, game):
        return self.generate_moves(x0, y0, board, deltas=diagonals)


class Rook(Figure):
    def __init__(self, name, color, game):
        super().__init__(name, color, game)
        self.castling = False

    def __eq__(self, other):
        return super().__eq__(other) and self.castling == other.castling

    def possible_moves(self, x0, y0, board, game):
        moves = self.generate_moves(x0, y0, board, deltas=straights)
        if not self.was_moved:
            moves += self.get_castling(game)
        return moves

    def get_castling(self, game):
        moves = []
        if not self.was_moved:
            if self.color == "white":
                king = game.figures.get((5, 1), None)
                if king is not None and not king.was_moved:
                    moves.append((5, 1))
            else:
                king = game.figures.get((5, 8), None)
                if king is not None and not king.was_moved:
                    moves.append((5, 8))

        if len(moves) > 0 and not game.is_checking_mode:
            self.castling = True
        return moves


class Pawn(Figure):
    def __init__(self, name, color, game):
        super().__init__(name, color, game)
        self.en_passant = False
        self.direction = self.game.direction

    def __eq__(self, other):
        return super().__eq__(other) and self.en_passant == other.en_passant

    def possible_moves(self, x, y, board, game):
        moves = []
        y1 = y + self.direction[self.color]

        # "attack diagonal"
        if self.attack_is_possible(x + 1, y1, board):
            moves.append((x + 1, y1))
        if self.attack_is_possible(x - 1, y1, board):
            moves.append((x - 1, y1))

        # "moving forward"
        y2 = y + 2 * self.direction[self.color]
        if (x, y1) not in board and Figure.is_inside(x, y1):
            moves.append((x, y1))

            if not self.was_moved and (x, y2) not in board and \
                    Figure.is_inside(x, y2):
                moves.append((x, y2))

        if game.have_once_moved_pawn and game.pawn_coord is not None:
            moves += self.get_extra_moves(x, y, game)
        return moves

    def attack_is_possible(self, x, y, board):
        return Figure.is_inside(x, y) and \
               (x, y) in board and board[(x, y)].color != self.color

    def get_check_moves(self, x, y):
        return [(x + 1, y + self.direction[self.color]),
                (x - 1, y + self.direction[self.color])]

    def get_extra_moves(self, x, y, game):
        # """Проверяем, есть ли возможность взятия на проходе"""
        move = self.get_medium_field(game.pawn_coord)
        if move is None or move in game.figures:
            return []
        if y + self.direction[self.color] == move[1]:
            if x + 1 == move[0] or x - 1 == move[0]:
                if not game.is_checking_mode:
                    self.en_passant = True
                return [move]
        return []

    @staticmethod
    def get_medium_field(coord_list):
        start = coord_list[0]
        end = coord_list[1]
        if start[0] != end[0]:
            return None
        if end[1] - start[1] == 2:
            return start[0], end[1] - 1
        if start[1] - end[1] == 2:
            return start[0], end[1] + 1
        return None


class Painter(Figure):
    def __init__(self, name, color, game):
        super().__init__(name, color, game)
        self.done_steps = 0
        self.wait_steps = 0

    def __eq__(self, other):
        return super().__eq__(other) and (self.wait_steps, self.done_steps) \
               == (other.wait_steps, other.done_steps)

    def possible_moves(self, x0, y0, board, game):
        if self.wait_steps > 0:
            return []
        if game.is_checking_mode:
            part_moves = \
                [(x, y) for x, y in self.get_permutations_step1(x0, y0)
                 if self.is_inside(x, y)]
            part2_moves = []
            for x1, y1 in part_moves:
                part2_moves += self.get_permutations_step2(x1, y1)
            return [(x2, y2) for x2, y2 in part2_moves
                    if self.is_inside(x2, y2) and
                    (x2, y2) not in game.figures and
                    not self.is_neighbour_cell(x0, y0, x2, y2)]
        elif self.done_steps == 0:
            # "x0, y0 - точка старта"
            return [(x, y) for x, y in self.get_permutations_step1(x0, y0)
                    if self.is_inside(x, y)]
        elif self.done_steps == 1:
            # "x0, y0 - точка промежуточного 'толчка', x, y - точка старта"
            x = game.painter_moved_partly[self.color][0][0]
            y = game.painter_moved_partly[self.color][0][1]
            # print([(x1, y1) for x1, y1 in self.get_permutations_step2(x0, y0)
            #       if self.is_inside(x1, y1) and
            #       (x1, y1) not in game.figures and
            #       not self.is_neighbour_cell(x, y, x1, y1)])
            return [(x1, y1) for x1, y1 in self.get_permutations_step2(x0, y0)
                    if self.is_inside(x1, y1) and
                    (x1, y1) not in game.figures and
                    not self.is_neighbour_cell(x, y, x1, y1)]
        else:
            return []

    @staticmethod
    def is_neighbour_cell(x0, y0, x1, y1):
        return abs(x0 - x1) <= 1 and abs(y0 - y1) <= 1

    @staticmethod
    def get_medium_field(start, end):
        return Painter.get_between_number(start[0], end[0]), \
               Painter.get_between_number(start[1], end[1])

    @staticmethod
    def get_between_number(c1, c2, ):
        if c2 > c1:
            return c1 + 1
        elif c1 == c2:
            return c1
        else:
            return c2 + 1

    @staticmethod
    def get_permutations_step1(x, y):
        return [(x + 2, y), (x + 2, y + 2), (x + 2, y - 2), (x, y + 2),
                (x, y - 2), (x - 2, y), (x - 2, y + 2), (x - 2, y - 2)]

    @staticmethod
    def get_permutations_step2(x, y):
        return [(x + 1, y), (x, y + 1), (x, y - 1), (x - 1, y)]
