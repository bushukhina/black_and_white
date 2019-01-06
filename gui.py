from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QBrush, QColor, QPixmap
from PyQt5.QtCore import Qt, QBasicTimer

from os import getcwd
import os
import sys

from game_units.args_wrap import ArgsWrap
from game_units.game_board import Board
from game_units.point import Point
from game_units.figures import *

white = "white"
black = "black"
short_figures = {Queen: "q", Bishop: "b", Knight: "n", Rook: "r", Pawn: "p", King: "k"}


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
        self.parent.set_status()

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
        elif self.board.move_is_correct(self.chosen_figure, self.start, chosen_point):
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
        message = str(self.board.game_state) + "."
        message += 'Start new game?'
        ask_game = QMessageBox.question(self,
                                        'End game',
                                        message,
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.Yes)
        if ask_game == QMessageBox.Yes:
            self.parent.show_dialog()

    def real_point_to_game_point(self, point_loc):
        return (point_loc.x // self.fig_width + 1), \
               8 - (point_loc.y // self.fig_height)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_board(qp)
        self.draw_figures(qp)
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
        brush.setColor(QColor(0, 0, 0))
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
            if type(fig) == Painter:
                self.draw_painter(qp, pos)
                continue
            pixmap = QPixmap(Chess.get_img_path(fig.color, type(fig)))

            pos = pos[0] - 1, pos[1] - 1
            qp.drawPixmap(pos[0] * self.fig_width,
                          self.height - pos[1] * self.fig_height - 80,
                          self.fig_width, self.fig_height, pixmap)

    @staticmethod
    def get_img_path(color, f_type):
        return os.path.join("img", color[0] + short_figures[f_type] + ".png")

    def draw_painter(self, qp, pos):
        brush = QBrush(Qt.SolidPattern)
        if self.board.figures[pos].color == black:
            brush.setColor(QColor(40, 40, 40))
            qp.setBrush(brush)
        else:
            brush.setColor(QColor(255, 255, 255))
            qp.setBrush(brush)

        pos = pos[0] - 1, pos[1] - 1
        qp.drawEllipse(pos[0] * self.fig_width,
                       self.height - pos[1] * self.fig_height - 80,
                       self.fig_width,
                       self.fig_height)


class Game(QMainWindow):
    def __init__(self, parent, board):
        super().__init__()
        self.parent = parent
        self.board = board
        self.statusBar().showMessage(self.board.player + self.board.inform_check())
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

        self.setGeometry(300, 30, 650, 670)
        self.show()

    def save_data(self):
        self.board.set_save()

    def closeEvent(self, e):
        self.board.save_log()
        self.parent.setVisible(True)

    def set_status(self):
        self.statusBar().showMessage("Turn:"+self.board.player +". "+ self.board.inform_check())


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
        self.table = None
        self.height = 300
        self.width = 300
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

    def show_dialog(self):
        self.dialog = StartDialog(self)
        self.dialog.show()

    def close_table(self):
        if self.table is not None:
            self.table.close()

    def start_game(self, arg):
        self.close_table()
        self.setVisible(False)
        arg.load = self.load
        self.load = None
        board = Board(arg)
        self.table = Game(self, board)

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
                error_dialog.showMessage("Can't load this game!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = Menu()
    sys.exit(app.exec_())
