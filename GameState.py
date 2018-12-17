from enum import Enum


class GameState(Enum):
    whiteWin = 1
    blackWin = 2
    draw = 3
    notFinished = 4

