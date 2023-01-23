import copy
import random

###############################
### GAME AND PLAYER CLASSES ###
###############################

class Player:
    def __init__(self, is_human=True, player=1):
        self.is_human = is_human
        self.player = player
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
    def __init__(self, is_human=False, player=2):
        self.is_human = is_human
        self.player = player

    def next_move(self, game, possible_moves):
        return self.random_move(possible_moves)

        # Random move
    def random_move(self, possible_moves):
        print("random move ...")
        l = len(possible_moves)
        return possible_moves[random.randint(0, l - 1)]


class AiGreedy(AiRandom):
    def __init__(self, is_human=False, player=2):
        self.is_human = is_human
        self.player = player

    def next_move(self, game, possible_moves):
        return self.greedy_move(game, possible_moves)

    # Greedy move
    def greedy_move(self, game, possible_moves):
        print("greedy move ...")
        # print("Possible moves: ", possible_moves)
        top_move_score = 0
        top_move = None
        for move in possible_moves:
            new_board = self.make_move(copy.deepcopy(game.board), self.player, move)
            score_p1, score_p2 = self.get_scores(new_board)
            if self.player == 1:
                move_score = score_p1
            else:
                move_score = score_p2
            if move_score > top_move_score:
                top_move = move
                top_move_score = move_score
        print("Best greedy move yields a score: ", top_move_score)
        return top_move


class AiGreedyPlus(AiGreedy):
    def __init__(self, is_human=False, player=2):
        self.is_human = is_human
        self.player = player

    def next_move(self, game, possible_moves):
        return self.greedy_plus_move(game, possible_moves)

    # Greedy move plus power and bad spots
    def greedy_plus_move(self, game, possible_moves):
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
        move = self.greedy_move(game, possible_moves)

        # in case all moves are bad and where elminated
        if not move:
            print("No moves left after bad moves clean up! Regular greedy move.")
            move = self.greedy_machine_move(game.board, game.current_player)
        # No power moves, just go for greedy
        return move


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


    def get_opponent(self, player):
        if player == 1:
            return 2
        else:
            return 1

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

    def get_possible_moves(self, board, player):
        possible_moves = []
        for r in range(8):
            for c in range(8):
                move = (r, c)
                if self.is_legal_move(board, player, move):
                    possible_moves.append(move)
        return possible_moves

    # checks for a legal move by going in the direction determined by col_dir and row_dir
    def check_dir(self, board, player, opponent, row, col, row_dir, col_dir):
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

    def is_legal_move(self, board, player, move):
        # print(f"Player: {player}, move: {move} is legal?")
        row, col = move
        if not board[row][col] == 0:
            return False

        opponent = self.get_opponent(player)

        # try west, east, north, south, northwest, ...
        col_row_dir = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (1, 1), (-1, 1)]
        for col_row in col_row_dir:
            col_dir, row_dir = col_row
            if self.check_dir(board, player, opponent, row, col, row_dir, col_dir):
                # print(f"Legal move.")
                return True
        # print(f"Illegal move.")
        return False

    def build_end_message(self, scores):
        score1, score2 = scores
        # Build End message and scores
        if score1 > score2:
            message = f"Game Over: Player #1 wins!"
            winning_player = 1
        elif score1 < score2:
            message = f"Game Over: Player #2 wins!"
            winning_player = 2
        else:
            message = f"Game Over: Draw!"
            winning_player = 0
        return message, winning_player

