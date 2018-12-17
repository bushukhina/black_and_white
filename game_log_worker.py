import os


class GameLogWorker:
    def __init__(self, file):
        if file is not None:
            # and os.path.isfile(file):
            self.file = file
        else:
            count = 0
            file = './log/log.txt'
            while os.path.isfile(file):
                count += 1
                file = './log/log' + str(count) + '.txt'
            self.file = file
            with open(self.file, 'w') as f:
                f.write('')

    def write(self, start, end):
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
        os.remove(self.file)


# glw = GameLogWorker()
# glw.write((1, 2), (1, 4))
# glw.write((1, 7), (1, 7))
# glw.write("undo", None)
# print(glw.load())
# import time
# time.sleep(10)
# glw.delete_file()
