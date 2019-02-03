import os


class GameLogWorker:
    def __init__(self, file):
        if file is not None:
            self.file = file
        else:
            count = 0
            file = os.path.join('log', 'log' + str(count) + '.txt')
            while os.path.isfile(file):
                count += 1
                file = os.path.join('log', 'log' + str(count) + '.txt')
            self.file = file
            with open(self.file, 'w') as f:
                f.write('')

    def write(self, start, end):
        """Логгирование ходов игры в формате: начало конец.
        Каждый ход в новой строке."""
        if start == 'undo' or start == 'redo':
            with open(self.file, 'a') as f:
                f.write(start + " " + "None" + "\n")
        else:
            start = chr(start[0] + ord('`')) + str(start[1])
            end = chr(end[0] + ord('`')) + str(end[1])
            with open(self.file, 'a') as f:
                f.write(start + " " + end + "\n")

    def load(self):
        game_moves = []
        with open(self.file, 'r') as f:
            for line in f:
                if len(line) > 0:
                    start, end = line.split()
                    if start == 'undo' or start == 'redo':
                        game_moves.append((start, None))
                    else:
                        start = ord(start[0]) - ord('`'), int(start[1])
                        end = ord(end[0]) - ord('`'), int(end[1])
                        game_moves.append((start, end))
        return game_moves[::-1]

    def delete_file(self):
        if os.path.isfile(self.file):
            os.remove(self.file)
