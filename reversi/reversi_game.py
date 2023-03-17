import copy
import random

###############################
### GAME AND PLAYER CLASSES ###
###############################

class Player:
    def __init__(self, is_human=True, role=None):
        self.is_human = is_human
        self.role = role
        self.move = None

    def get_opponent(self, player):
        if player == 1:
            return 2
        else:
            return 1

    def next_move(self):
        return self.move

    # method needed to calculate theoretical possible outcomes of every move
    def make_move(self, board, player, move):
        # print(f"Player: {player}, makes move: {move}")
        row, col = move
        opponent = self.get_opponent(player)

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

    def get_scores(self, board):
        p1 = 0
        p2 = 0
        for r in range(8):
            for c in range(8):
                if board[r][c] == 1:
                    p1 += 1
                elif board[r][c] == 2:
                    p2 += 1
        return p1, p2


class AiRandom(Player):
    def __init__(self, is_human=False, role=None):
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
            score_p1, score_p2 = self.get_scores(new_board)
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

        # make a greedy move with the remaining possible, moves
        move = self.greedy_move(board, possible_moves)

        # in case all moves are bad and where elminated
        if not move:
            print("No moves left after bad moves clean up! Regular greedy move.")
            move = self.greedy_move(board, self.role)
        # No power moves, just go for greedy
        return move


class AiMiniMax(AiGreedy):
    def __init__(self, is_human=False, role=None):
        self.is_human = is_human
        self.role = role

    def next_move(self, board, possible_moves):
        return self.minimax_move(board, possible_moves)

    # Implementation of the Minimax algorithm
    def minimax_move(self, board, possible_moves):
        depth = 4
        print(f"Minimax move with depth {depth}...")
        possible_moves = get_possible_moves(board, self.role)
        player = self.role
        minimax_moves = []
        for move in possible_moves:
            new_board = self.make_move(copy.deepcopy(board), player, move)
            score = self.minimax(new_board, self.role, depth, True)
            minimax_moves.append((move, score))
        print(minimax_moves)
        minimax_moves = sorted(minimax_moves, key=lambda x: x[1], reverse=True)

        return_move = minimax_moves[0][0]
        print(f"Returning move: {return_move}")
        return return_move

    def minimax(self, board, player, depth, maximizingPlayer):
        # print(f"Current depth: {depth}")
        if depth == 0 or self.game_over_position(board, player):
            return self.get_abs_score(board, player)

        possible_moves = get_possible_moves(board, player)
        if maximizingPlayer:
            max_eval = -64
            for move in possible_moves:
                new_board = self.make_move(copy.deepcopy(board), player, move)
                eval = self.minimax(new_board, player, depth-1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = +64
            for move in possible_moves:
                new_board = self.make_move(copy.deepcopy(board), self.get_opponent(player), move)
                eval = self.minimax(new_board, self.get_opponent(player), depth-1, False)
                min_eval = min(min_eval, eval)
            return min_eval

    def get_abs_score(self, board, player):
        score_p1, score_p2 = self.get_scores(board)
        if player == 1:
            score = score_p1 - score_p2
        else:
            score = score_p2 - score_p1
        return score

    def game_over_position(self, board, player):
        possible_moves = get_possible_moves(board, player)
        if len(possible_moves) == 0:
            next_possible_moves = get_possible_moves(board, self.get_opponent(player))
            if len(next_possible_moves) == 0:
                print("Game Over Position found!")
                return True
        return False

class Node:
    def __init__(self, parent_node, move, board, score):
        self.parent_node = parent_node
        self.move = move
        self.board = board
        self.score = score
    def __repr__(self):
        return f"{self.move} with score {self.score}"

class Game:
    def __init__(self, player1, player2, difficulty, board=None):
        if board is None:
            self.board = [[0, 0, 0, 0, 0, 0, 0, 0] for x in range(8)]
            self.board[3][3] = 2
            self.board[4][4] = 2
            self.board[3][4] = 1
            self.board[4][3] = 1
        else:
            self.board = board

        self.player1_name = player1
        self.player2_name = player2
        self.difficulty = difficulty


def get_opponent(player):
    if player == 1:
        return 2
    else:
        return 1

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