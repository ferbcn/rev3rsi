# Defines special boards for testing game functionality

class TestGameP1LastMoveToDraw():
    def __init__(self):
        self.board = [[2, 2, 2, 0, 0, 1, 1, 1] for x in range(8)]
        self.board[0][5] = 0
        self.board[0][6] = 2

        self.player1 = "human"
        self.player2 = "machine"
        self.machine_type = "greedy"
        self.human_player = 1


class TestGameP1LastMoveToWin():
    def __init__(self):
        self.board = [[2, 2, 2, 0, 0, 1, 1, 1] for x in range(8)]
        self.board[0][5] = 2

        self.player1 = "human"
        self.player2 = "machine"
        self.machine_type = "greedy"
        self.human_player = 1


class TestGameP1LastMoveToLose():
    def __init__(self):
        self.board = [[2, 2, 2, 0, 0, 0, 1, 1] for x in range(8)]
        self.board[0][5] = 2

        self.player1 = "human"
        self.player2 = "machine"
        self.machine_type = "greedy"
        self.human_player = 1


class TestGameP1MoveP2LastMoveToLose():
    def __init__(self):
        self.board = [[2, 2, 2, 0, 0, 0, 1, 1] for x in range(8)]
        self.board[0][5] = 2
        self.board[7][3] = 1

        self.player1 = "human"
        self.player2 = "machine"
        self.machine_type = "greedy"
        self.human_player = 1


class TestGameP1MoveP2LastMoveToWin():
    def __init__(self):
        self.board = [[2, 2, 0, 0, 0, 1, 1, 1] for x in range(8)]
        self.board[0][4] = 2
        self.board[7][2] = 1

        self.player1 = "human"
        self.player2 = "machine"
        self.machine_type = "greedy"
        self.human_player = 1
