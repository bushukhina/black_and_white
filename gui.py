from PyQt5.QtWidgets import QFrame, QMessageBox, QAction, QDialog, QMainWindow, QLabel, \
    QComboBox, QPushButton, QErrorMessage, QApplication, QFileDialog
from PyQt5.QtGui import QPainter, QBrush, QColor, QPixmap
from PyQt5.QtCore import Qt, QBasicTimer

from os import getcwd
import os
import sys

from game_units.args_wrap import ArgsWrap
from game_units.game_board import Board
from game_units.point import Point
from game_units.figures import *

WHITE = "white"
BLACK = "black"
short_figures = {Queen: "q", Bishop: "b", Knight: "n",
                 Rook: "r", Pawn: "p", King: "k"}


class Chess(QFrame):
    def __init__(self, parent, board):
        super().__init__()
        self.board = board
        self.parent = parent

        self.height = 640
        self.width = 640
        self.rows = 8
        self.columns = 8

        self.mouse_location = Point(0, 0)
        self.chosen_figure = None
        self.start = (-1, -1)

        self.unit_ui()

    def unit_ui(self):
        self.timer = QBasicTimer()
        self.timer.start(800, self)
        self.setMouseTracking(True)
        self.resize(self.width, self.height)
        self.show()

    @property
    def fig_height(self):
        return self.height // self.columns

    @property
    def fig_width(self):
        return self.width // self.rows

    def closeEvent(self, e):
        self.parent.close()

    def timerEvent(self, e):
        if self.board.finish_the_game():
            self.end_game()
        if not self.board.is_ai_move():
            return
        self.board.bot_make_move()
        self.update()

    def mouseMoveEvent(self, e):
        self.mouse_location.x = e.x()
        self.mouse_location.y = e.y()

    def mousePressEvent(self, e):
        if self.board.is_ai_move() or self.board.finish_the_game():
            return
        chosen_point = self.real_point_to_game_point(self.mouse_location)
        if self.chosen_figure is None:
            self.chosen_figure = self.board.get_moving_figure(chosen_point)
            self.start = chosen_point
        elif self.board.move_is_correct(self.chosen_figure,
                                        self.start, chosen_point):
            if self.board.is_last_line(chosen_point):
                self.show_dialog()
            self.board.move(self.chosen_figure, self.start, chosen_point)
            self.chosen_figure = None
            self.start = (-1, -1)
            self.parent.set_status()
        else:
            self.chosen_figure = self.board.get_moving_figure(chosen_point)
            self.start = chosen_point
        self.update()

    def end_game(self):
        self.timer.stop()
        message = str(self.board.game_state) + "." + 'Start new game?'
        ask_game = QMessageBox.question(self,
                                        'End game',
                                        message,
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.Yes)
        if ask_game == QMessageBox.Yes:
            self.parent.show_dialog()

    def real_point_to_game_point(self, point_loc):
        pos = (point_loc.x // self.fig_width + 1), \
               8 - (point_loc.y // self.fig_height)
        if self.board.player == BLACK:
            pos = 8 - pos[0] + 1, 8 - pos[1] + 1
        return pos

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        try:
            self.draw_board(qp)
            self.draw_figures(qp)
        finally:
            qp.end()

    def draw_board(self, qp):
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(QColor(210, 210, 210))
        qp.setBrush(brush)
        for i in range(self.rows):
            for j in range(i % 2, self.columns, 2):
                qp.drawRect(i * self.fig_width,
                            j * self.fig_height,
                            self.fig_width,
                            self.fig_height)
        brush.setColor(QColor(145, 67, 12))
        qp.setBrush(brush)
        for i in range(self.rows):
            for j in range((i + 1) % 2, self.columns, 2):
                qp.drawRect(i * self.fig_width,
                            j * self.fig_height,
                            self.fig_width,
                            self.fig_height)

    def draw_figures(self, qp):
        for pos in self.board.figures.keys():
            fig = self.board.figures[pos]
            if isinstance(fig, Painter):
                self.draw_painter(qp, pos)
                continue
            pixmap = QPixmap(Chess.get_img_path(fig.color, type(fig)))

            if self.board.player == WHITE:
                pos = pos[0] - 1, pos[1] - 1
            else:
                pos = 8 - pos[0], 8 - pos[1]
            qp.drawPixmap(pos[0] * self.fig_width,
                          self.height - pos[1] * self.fig_height - 80,
                          self.fig_width, self.fig_height, pixmap)

    @staticmethod
    def get_img_path(color, f_type):
        return os.path.join("img", color[0] + short_figures[f_type] + ".png")

    def draw_painter(self, qp, pos):
        brush = QBrush(Qt.SolidPattern)
        if self.board.figures[pos].color == BLACK:
            brush.setColor(QColor(30, 30, 30))
            qp.setBrush(brush)
        else:
            brush.setColor(QColor(255, 255, 255))
            qp.setBrush(brush)

        if self.board.player == WHITE:
            pos = pos[0] - 1, pos[1] - 1
        else:
            pos = 8 - pos[0], 8 - pos[1]
        qp.drawEllipse(pos[0] * self.fig_width,
                       self.height - pos[1] * self.fig_height - 80,
                       self.fig_width,
                       self.fig_height)

    def set_figure(self, arg):
        self.board.set_figure_type(arg)

    def show_dialog(self):
        figure_dialog = FigureDialog(self)
        figure_dialog.exec_()


class Game(QMainWindow):
    def __init__(self, parent, board):
        super().__init__()
        self.parent = parent
        self.board = board
        self.statusBar().showMessage("Turn: " + self.board.player +
                                     '.Chess board ' +
                                     str(self.parent.index + 1))
        self.chess_game = Chess(self, board)
        self.setCentralWidget(self.chess_game)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Checkers')
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        new_act = QAction('New', self)
        new_act.setShortcut('Ctrl+N')
        new_act.triggered.connect(self.parent.show_dialog)

        exit_act = QAction('Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.triggered.connect(self.close)

        save_act = QAction('Save', self)
        save_act.setShortcut('Ctrl+S')
        save_act.triggered.connect(self.save_data)

        load_act = QAction('Load', self)
        load_act.setShortcut('Ctrl+L')
        load_act.triggered.connect(self.parent.load_game)

        file_menu.addAction(new_act)
        file_menu.addAction(save_act)
        file_menu.addAction(load_act)
        file_menu.addAction(exit_act)

        file_menu2 = menu_bar.addMenu("&Edit")

        redo_act = QAction('Redo', self)
        redo_act.setShortcut('Ctrl+Shift+Z')
        redo_act.triggered.connect(self.board.redo)

        undo_act = QAction('Undo', self)
        undo_act.setShortcut('Ctrl+Z')
        undo_act.triggered.connect(self.board.undo)

        file_menu2.addAction(redo_act)
        file_menu2.addAction(undo_act)

        file_menu3 = menu_bar.addMenu("&Change board")

        add_act = QAction('Add new board', self)
        add_act.setShortcut('Ctrl+Shift+N')
        add_act.triggered.connect(self.add_board)

        next_act = QAction('Next board', self)
        next_act.setShortcut('Ctrl+Tab')
        next_act.triggered.connect(self.next_board)

        file_menu3.addAction(add_act)
        file_menu3.addAction(next_act)

        self.setGeometry(300, 30, 645, 680)
        self.setFixedSize(self.size())
        self.show()

    def add_board(self):
        if len(self.parent.games) < 4:
            self.setVisible(False)
            self.parent.add_game()

    def next_board(self):
        if len(self.parent.games) > 1:
            self.setVisible(False)
            self.parent.next_game()

    def save_data(self):
        self.board.set_save()

    def closeEvent(self, e):
        self.board.save_log()
        self.parent.setVisible(True)

    def set_status(self):
        self.statusBar().showMessage("Turn: " + self.board.player +
                                     " . " + self.board.inform_check())


class FigureDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def parse_args(self):
        f_text = self.f_box.currentText()[0]
        self.parent.set_figure(f_text)
        self.close()

    def init_ui(self):
        text1 = "Now you can make your pawn to be queen, knight, " \
                "rook or bishop."
        text2 = "Or you can leave it pawn."

        self.some_text = QLabel(text1, self)
        self.some_text.move(20, 20)
        self.some_text2 = QLabel(text2, self)
        self.some_text2.move(20, 40)

        self.f_text = QLabel('Pawn will become:', self)
        self.f_text.move(70, 100)

        self.f_box = QComboBox(self)
        self.f_box.addItem('qween')
        self.f_box.addItem('knight')
        self.f_box.addItem('rook')
        self.f_box.addItem('bishop')
        self.f_box.addItem('pawn')
        self.f_box.move(170, 100)

        self.button_ok = QPushButton('Ok', self)
        self.button_ok.move(170, 150)
        self.button_ok.clicked.connect(self.parse_args)

        self.setWindowTitle('Choose figure"s new type')
        self.resize(360, 200)
        self.show()


class StartDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def parse_args(self):
        mode = self.mode_box.currentText()
        use_painter = self.p_box.currentText() == "Yes"
        endless = self.step_box.currentText() == "Yes"

        arg = ArgsWrap(None, mode, endless, use_painter)
        self.parent.start_game(arg)
        self.close()

    def init_ui(self):
        self.mode_text = QLabel('Game mode', self)
        self.mode_text.move(70, 20)

        self.mode_box = QComboBox(self)
        self.mode_box.addItem('H-H')
        self.mode_box.addItem('H-AI')
        self.mode_box.addItem('AI-H')
        self.mode_box.addItem('AI-AI')
        self.mode_box.move(40, 50)

        self.p_text = QLabel('Use painter', self)
        self.p_text.move(230, 20)

        self.p_box = QComboBox(self)
        self.p_box.addItem('No')
        self.p_box.addItem('Yes')
        self.p_box.move(200, 50)

        self.step_text = QLabel('Stop after 85 steps', self)
        self.step_text.move(120, 90)

        self.step_box = QComboBox(self)
        self.step_box.addItem('No')
        self.step_box.addItem('Yes')
        self.step_box.move(140, 120)

        self.button_ok = QPushButton('Ok', self)
        self.button_ok.move(50, 150)
        self.button_ok.clicked.connect(self.parse_args)

        self.button_cancel = QPushButton('Cancel', self)
        self.button_cancel.clicked.connect(self.close)
        self.button_cancel.move(200, 150)

        self.setWindowTitle('Start game')
        self.resize(360, 200)
        self.show()


class Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load = None
        self.games = []
        self.index = 0
        self.table = None
        self.height = 300
        self.width = 300
        self.adding = False
        self.init_ui()

    def init_ui(self):

        self.statusBar().showMessage('Welcome!')
        self.setWindowTitle('Chess')

        start_button = QPushButton('Start', self)
        start_button.move(100, 30)
        start_button.setToolTip('Open setup game')
        start_button.clicked.connect(self.show_dialog)

        load_button = QPushButton('Load', self)
        load_button.move(100, 80)
        load_button.setToolTip('Load old game')
        load_button.clicked.connect(self.load_game)

        exit_button = QPushButton('Exit', self)
        exit_button.move(100, 130)
        exit_button.setToolTip('Close window')
        exit_button.clicked.connect(self.close)

        self.setGeometry(150, 150, 300, 200)
        self.show()
        self.start_game(ArgsWrap(None, 'H-H', False, False))

    def increase_index(self):
        self.index = (self.index + 1) % len(self.games)

    def add_game(self):
        self.adding = True
        self.setVisible(True)

    def next_game(self):
        self.increase_index()
        self.table = self.games[self.index]
        self.table.setVisible(True)

    def show_dialog(self):
        self.dialog = StartDialog(self)
        self.dialog.show()

    # def close_table(self):
    #     if self.table is not None:
    #         self.table.close()
    #         self.table = None

    def start_game(self, arg):
        if not self.adding:
            for g in self.games:
                g.close()
            self.table = None
            self.index = 0
            self.games = []
        self.adding = False
        self.setVisible(False)
        arg.load = self.load
        self.load = None
        board = Board(arg)
        self.table = Game(self, board)
        self.games.append(self.table)
        self.increase_index()

    def load_game(self):
        path = os.path.join(getcwd(), 'log')
        filename = QFileDialog.getOpenFileName(self, 'Load game', path)
        if filename:
            try:
                self.load = filename[0]
                self.show_dialog()
            except Exception as e:
                error_dialog = QErrorMessage(self)
                error_dialog.setWindowTitle('Error!')
                error_dialog.showMessage("Can't load this game. "
                                         "Exception text:" + str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = Menu()
    sys.exit(app.exec_())
