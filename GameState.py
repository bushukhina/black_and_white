from enum import Enum


class GameState(Enum):
    whiteWin = 1
    blackWin = 2
    drawSameState3Times = 3
    notFinished = 4
    drawWhitePat = 5
    drawBlackPat = 6
    drawStep85 = 7
