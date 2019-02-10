from enum import Enum


class GameState(Enum):
    WHITE_WIN = 1
    BLACK_WIN = 2
    DRAW_REPEAT_STATE = 3
    NOT_FINISHED = 4
    DRAW_WHITE_PAT = 5
    DRAW_BLACK_PAT = 6
    DRAW_85_STEPS = 7
