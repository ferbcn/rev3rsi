import copy
import random
import sys
import time


# maximum time the AI is allowed to think (seconds)
MAX_TIME = 1
MAX_DEPTH = 30

###########################
# GAME AND PLAYER CLASSES #
###########################


class Player:
    def __init__(self, is_human=True, role=None):
        self.is_human = is_human
        self.role = role
        self.move = None

    # method needed to calculate theoretical possible outcomes of every move
    def make_move(self, board, player, move):
        # print(f"Player: {player}, makes move: {move}")
        row, col = move
        opponent = get_opponent(player)

        # try west, east, north, south, northwest, ...
        col_row_dir = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (1, 1), (-1, 1)]

        for col_row in col_row_dir:
            col_dir, row_dir = col_row
            # print("filling dir... ", col_row)
            board = self.fill_dir(board, player, opponent, row, col, row_dir, col_dir)

        return board

    def fill_dir(self, board, player, opponent, row, col, row_dir, col_dir):
        opponent_inside = False
        col_iter = col + col_dir
        row_iter = row + row_dir
        while 0 <= col_iter <= 7 and 0 <= row_iter <= 7:
            # print("iterating:", col_iter, row_iter)
            if opponent_inside and board[row_iter][col_iter] == player:
                # bingo! fill this direction
                # print("filling dir found! (col/row):", col_dir, row_dir)
                col_fill = col + col_dir
                row_fill = row + row_dir
                while board[row_fill][col_fill] == opponent:
                    board[row_fill][col_fill] = player
                    col_fill = col_fill + col_dir
                    row_fill = row_fill + row_dir
                board[row][col] = player
                # print("dir filled succsfully!")
                break
            elif board[row_iter][col_iter] == opponent:
                opponent_inside = True
            col_iter = col_iter + col_dir
            row_iter = row_iter + row_dir
        return board


class AiFirst(Player):
    def __init__(self, is_human=False, role=None):
        super().__init__(is_human, role)
        self.is_human = is_human
        self.role = role

    def next_move(self, board, possible_moves):
        return self.dumb_move(possible_moves)

        # Random move
    def dumb_move(self, possible_moves):
        print("dumb move (first of list)...")
        return possible_moves[0]


class AiLast(Player):
    def __init__(self, is_human=False, role=None):
        super().__init__(is_human, role)
        self.is_human = is_human
        self.role = role

    def next_move(self, board, possible_moves):
        return self.dumb_move(possible_moves)

        # Random move
    def dumb_move(self, possible_moves):
        print("dumb move (first of list)...")
        return possible_moves[-1]


class AiWorst(Player):
    def __init__(self, is_human=False, role=None):
        super().__init__(is_human, role)
        self.is_human = is_human
        self.role = role

    def next_move(self, board, possible_moves):
        return self.greedy_move(board, possible_moves)

    # Greedy move
    def greedy_move(self, board, possible_moves):
        print("worst move ...")
        # print("Possible moves: ", possible_moves)
        worst_move_score = 0
        worst_move = None
        for move in possible_moves:
            new_board = self.make_move(copy.deepcopy(board), self.role, move)
            score_p1, score_p2 = get_scores(new_board)
            if self.role == 1:
                move_score = score_p2
            else:
                move_score = score_p1
            if move_score > worst_move_score:
                worst_move = move
                worst_move_score = move_score
        print("Worst move yields a score: ", worst_move_score)
        return worst_move


class AiRandom(Player):
    def __init__(self, is_human=False, role=None):
        super().__init__(is_human, role)
        self.is_human = is_human
        self.role = role

    def next_move(self, board, possible_moves):
        return self.random_move(possible_moves)

        # Random move
    def random_move(self, possible_moves):
        print("random move ...")
        l = len(possible_moves)
        return possible_moves[random.randint(0, l - 1)]


class AiGreedy(AiRandom):
    def __init__(self, is_human=False, role=None):
        super().__init__(is_human, role)
        self.is_human = is_human
        self.role = role

    def next_move(self, board, possible_moves):
        return self.greedy_move(board, possible_moves)

    # Greedy move
    def greedy_move(self, board, possible_moves):
        print("greedy move ...")
        # print("Possible moves: ", possible_moves)
        top_move_score = 0
        top_move = None
        for move in possible_moves:
            new_board = self.make_move(copy.deepcopy(board), self.role, move)
            score_p1, score_p2 = get_scores(new_board)
            if self.role == 1:
                move_score = score_p1
            else:
                move_score = score_p2
            if move_score > top_move_score:
                top_move = move
                top_move_score = move_score
        print("Best greedy move yields a score: ", top_move_score)
        return top_move


class AiGreedyPlus(AiGreedy):
    def __init__(self, is_human=False, role=None):
        super().__init__(is_human, role)
        self.is_human = is_human
        self.role = role

    def next_move(self, board, possible_moves):
        return self.greedy_plus_move(board, possible_moves)

    # Greedy move plus power and bad spots
    def greedy_plus_move(self, board, possible_moves):
        print("greedy plus move ...")
        power_spots = [(0, 0), (0, 7), (7, 0), (7, 7), (0, 2), (0, 5), (7, 2), (7, 5), (5, 7), (2, 7), (5, 0), (2, 0)]
        bad_spots = [(0, 1), (0, 6), (1, 7), (6, 7), (7, 6), (7, 1), (6, 0), (1, 0), (1, 1), (1, 6), (6, 6), (6, 1)]

        # checks for power moves in ordered way
        for pow_move in power_spots:
            for pos_move in possible_moves:
                if pow_move == pos_move:
                    print("POWER MOVE: ", pos_move)
                    return pos_move

        better_moves = []
        for move in possible_moves:
            if not move in bad_spots:
                better_moves.append(move)

        # make a greedy move (from parent class AIGreedy) with the remaining possible moves
        move = self.greedy_move(board, possible_moves)

        # in case all moves are bad and where eliminated
        if not move:
            print("No moves left after bad moves clean up! Regular greedy move.")
            move = self.greedy_move(board, self.role)
        # No power moves, just go for greedy
        return move


class AiMiniMax(AiGreedyPlus):
    def __init__(self, is_human=False, role=None, max_time=MAX_TIME, max_depth=MAX_DEPTH):
        super().__init__(is_human, role)
        self.max_time = max_time
        self.is_human = is_human
        self.role = role
        print("Minimax is player", self.role)
        self.start_time = 0
        self.max_depth = max_depth
        self.max_depth_reached = 0

    def next_move(self, board, possible_moves):
        scores = get_scores(board)
        if scores[0] + scores[1] < 33:
            return self.greedy_plus_move(board, possible_moves)
        return self.minimax_move(board)

    # Implementation of the Minimax algorithm
    def minimax_move(self, board):
        depth = 1
        print(f"Minimax move limited to {self.max_time} seconds...")
        possible_moves = get_possible_moves(board, self.role)
        player = self.role
        minimax_moves = []
        self.start_time = time.time()
        for move in possible_moves:
            self.max_depth_reached = depth
            new_board = self.make_move(copy.deepcopy(board), player, move)
            score = self.minimax(new_board, self.role, depth, -65, 65, True)
            minimax_moves.append((move, score))
        minimax_moves = sorted(minimax_moves, key=lambda x: x[1], reverse=True)
        print(minimax_moves)

        return_move = minimax_moves[0][0]
        print(f"Returning move: {return_move}")
        return return_move

    def minimax(self, board, player, depth, alpha, beta, maximizingPlayer):

        if depth > self.max_depth_reached:
            self.max_depth_reached = depth
            # print by substitution of the print statement below
            # print(f"Max depth reached: {depth}")
            sys.stdout.write(f"\rMax depth reached: {depth}")
            sys.stdout.flush()

        if depth > self.max_depth or self.game_over_position(board, player) or time.time()-self.start_time > self.max_time:
            abs_score = self.get_abs_score(board, self.role)
            return abs_score

        possible_moves = get_possible_moves(board, player)
        if maximizingPlayer:
            max_eval = -65
            for move in possible_moves:
                new_board = self.make_move(copy.deepcopy(board), player, move)
                eval = self.minimax(new_board, get_opponent(player), depth+1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = 65
            for move in possible_moves:
                new_board = self.make_move(copy.deepcopy(board), player, move)
                eval = self.minimax(new_board, get_opponent(player), depth+1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_abs_score(self, board, player):
        score_p1, score_p2 = get_scores(board)
        score = score_p1 - score_p2 if player == 1 else score_p2 - score_p1
        return score

    def game_over_position(self, board, player):
        possible_moves = get_possible_moves(board, player)
        if len(possible_moves) == 0:
            next_possible_moves = get_possible_moves(board, get_opponent(player))
            if len(next_possible_moves) == 0:
                """
                print("Game Over Position found!")
                for line in board: print(line)
                scores = self.get_scores(board)
                print(f"Score: {scores[0]}/{scores[1]}")
                """
                return True
        return False


class AiTop(Player):
    def __init__(self, is_human=False, role=None, max_time=MAX_TIME, max_depth=MAX_DEPTH):
        super().__init__(is_human, role)
        self.max_time = max_time
        self.is_human = is_human
        self.role = role
        self.start_time = 0
        self.max_depth = max_depth
        self.max_depth_reached = 0

    def next_move(self, board, possible_moves):
        return self.minimax_move(board)

    def minimax_move(self, board):
        depth = 1
        print(f"Minimax move limited to {self.max_time} seconds...")
        possible_moves = get_possible_moves(board, self.role)
        player = self.role
        minimax_moves = []
        self.start_time = time.time()
        for move in possible_moves:
            self.max_depth_reached = depth
            new_board = self.make_move(copy.deepcopy(board), player, move)
            score = self.minimax(new_board, self.role, depth, -65, 65, True)
            minimax_moves.append((move, score))
        minimax_moves = sorted(minimax_moves, key=lambda x: x[1], reverse=True)
        print(minimax_moves)

        return_move = minimax_moves[0][0]
        print(f"Returning move: {return_move}")
        return return_move

    def minimax(self, board, player, depth, alpha, beta, maximizingPlayer):
        if depth > self.max_depth_reached:
            self.max_depth_reached = depth
            sys.stdout.write(f"\rMax depth reached: {depth}")
            sys.stdout.flush()

        if depth > self.max_depth or self.game_over_position(board, player) or time.time() - self.start_time > self.max_time:
            abs_score = self.get_abs_score(board, self.role)
            return abs_score

        possible_moves = get_possible_moves(board, player)
        if maximizingPlayer:
            max_eval = -65
            for move in possible_moves:
                new_board = self.make_move(copy.deepcopy(board), player, move)
                eval = self.minimax(new_board, get_opponent(player), depth + 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = 65
            for move in possible_moves:
                new_board = self.make_move(copy.deepcopy(board), player, move)
                eval = self.minimax(new_board, get_opponent(player), depth + 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_abs_score(self, board, player):
        score_p1, score_p2 = get_scores(board)
        score = score_p1 - score_p2 if player == 1 else score_p2 - score_p1
        return score

    def game_over_position(self, board, player):
        possible_moves = get_possible_moves(board, player)
        if len(possible_moves) == 0:
            next_possible_moves = get_possible_moves(board, get_opponent(player))
            if len(next_possible_moves) == 0:
                return True
        return False


class AiMachinePlayerMaker:
    def __init__(self, level_name, role):
        self.machine_player = None
        if level_name == "first":
            self.machine_player = AiFirst(level_name, role)
        if level_name == "last":
            self.machine_player = AiLast(level_name, role)
        elif level_name == "random":
            self.machine_player = AiRandom(level_name, role)
        elif level_name == "worst":
            self.machine_player = AiWorst(level_name, role)
        elif level_name == "greedy":
            self.machine_player = AiGreedy(level_name, role)
        elif level_name == "greedy-plus":
            self.machine_player = AiGreedyPlus(level_name, role)
        elif level_name == "mini-max":
            self.machine_player = AiMiniMax(level_name, role)
        elif level_name == "mini-max-2s":
            self.machine_player = AiMiniMax(level_name, role, max_time=2)
        elif level_name == "mini-max-3s":
            self.machine_player = AiMiniMax(level_name, role, max_time=3)
        elif level_name == "top":
            self.machine_player = AiTop(level_name, role, max_time=3)

    def get_player(self):
        return self.machine_player


class Game:
    def __init__(self, player1, player2, difficulty, board=None):
        if board is None:
            self.board = [[0, 0, 0, 0, 0, 0, 0, 0] for x in range(8)]
            self.board[3][3] = 2
            self.board[3][4] = 2
            self.board[4][4] = 1
            self.board[4][3] = 1
        else:
            self.board = board

        self.player1_name = player1
        self.player2_name = player2
        self.difficulty = difficulty


def get_opponent(player):
    op = 2 if player == 1 else 1
    return op

def get_scores(board):
    p1 = 0
    p2 = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == 1:
                p1 += 1
            elif board[r][c] == 2:
                p2 += 1
    return p1, p2


def get_scores_from_string(board):
    p1 = 0
    p2 = 0
    for char in board:
        if char == "1":
            p1 += 1
        elif char == "2":
            p2 += 1
    return p1, p2

def get_possible_moves(board, player):
    possible_moves = []
    for r in range(8):
        for c in range(8):
            move = (r, c)
            if is_legal_move(board, player, move):
                possible_moves.append(move)
    return possible_moves

# checks for a legal move by going in the direction determined by col_dir and row_dir
def check_dir(board, player, opponent, row, col, row_dir, col_dir):
    opponent_inside = False
    col_iter = col + col_dir
    row_iter = row + row_dir
    while 0 <= col_iter <= 7 and 0 <= row_iter <= 7:
        # print(col_iter, row_iter, board[row_iter][col_iter], opponent_inside)
        if opponent_inside and board[row_iter][col_iter] == player:
            return True
        elif board[row_iter][col_iter] == opponent:
            opponent_inside = True
            col_iter = col_iter + col_dir
            row_iter = row_iter + row_dir
        else:
            return False


def is_legal_move(board, player, move):
    # print(f"Player: {player}, move: {move} is legal?")
    row, col = move
    if not board[row][col] == 0:
        return False
    opponent = get_opponent(player)
    # try west, east, north, south, northwest, ...
    col_row_dir = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (1, 1), (-1, 1)]
    for col_row in col_row_dir:
        col_dir, row_dir = col_row
        if check_dir(board, player, opponent, row, col, row_dir, col_dir):
            # print(f"Legal move.")
            return True
    # print(f"Illegal move.")
    return False


def human_move(board, human_player, move):
    # make a human move
    print("Human move: ", move)
    # make move and save board
    board = human_player.make_move(board, human_player.role, move)
    return move, board


def machine_move(board, machine_player):
    # make a machine move
    print("# Machine move #")
    possible_moves = get_possible_moves(board, machine_player.role)
    print(possible_moves)
    next_move = machine_player.next_move(board, possible_moves)
    print("Machine move: ", next_move)
    board = machine_player.make_move(board, machine_player.role, next_move)
    return next_move, board
