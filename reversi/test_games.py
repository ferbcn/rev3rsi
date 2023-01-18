# Defines special boards for testing game functionality
class TestGame:
    def __init__(self, player1, player2, difficulty):
        self.player1 = player1
        self.player2 = player2
        self.difficulty = difficulty
        self.current_player = 1


class TestGameP1LastMoveToDraw(TestGame):
    def __init__(self, player1, player2, difficulty):
        super().__init__(player1, player2, difficulty)

        self.board = [[2, 2, 2, 0, 0, 1, 1, 1] for x in range(8)]
        self.board[0][5] = 0
        self.board[0][6] = 2


class TestGameP1LastMoveToWin:
    def __init__(self):
        super().__init__(player1, player2, difficulty)
        self.board = [[2, 2, 2, 0, 0, 1, 1, 1] for x in range(8)]
        self.board[0][5] = 2


class TestGameP1LastMoveToLose():
    def __init__(self):
        super().__init__(player1, player2, difficulty)
        self.board = [[2, 2, 2, 0, 0, 0, 1, 1] for x in range(8)]
        self.board[0][5] = 2


class TestGameP1MoveP2LastMoveToLose():
    def __init__(self):
        super().__init__(player1, player2, difficulty)
        self.board = [[2, 2, 2, 0, 0, 0, 1, 1] for x in range(8)]
        self.board[0][5] = 2
        self.board[7][3] = 1


class TestGameP1MoveP2LastMoveToWin():
    def __init__(self):
        self.board = [[2, 2, 0, 0, 0, 1, 1, 1] for x in range(8)]
        self.board[0][4] = 2
        self.board[7][2] = 1
