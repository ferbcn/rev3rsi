import copy
import random

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# from django.core import serializers

from .models import GameDB, GameState

#from test_games import TestGameP1LastMoveToDraw

class Game():
    def __init__(self):
        self.board = [[0, 0, 0, 0, 0, 0, 0, 0] for x in range(8)]
        self.board[3][3] = 2
        self.board[4][4] = 2
        self.board[3][4] = 1
        self.board[4][3] = 1

        self.player1 = "human"
        self.player2 = "machine"
        self.machine_type = "greedy"
        self.human_player = 1


# checks for a legal move by going in the direction determined by col_dir and row_dir
def check_dir(board, player, oponent, row, col, row_dir, col_dir):
    oponent_inside = False
    col_iter = col + col_dir
    row_iter = row + row_dir
    while col_iter >= 0 and col_iter <= 7 and row_iter >= 0 and row_iter <= 7:
        # print(col_iter, row_iter, board[row_iter][col_iter], oponent_inside)
        if oponent_inside and board[row_iter][col_iter] == player:
            return True
        elif board[row_iter][col_iter] == oponent:
            oponent_inside = True
            col_iter = col_iter + col_dir
            row_iter = row_iter + row_dir
        else:
            return False


def fill_dir(board, player, oponent, row, col, row_dir, col_dir):
    oponent_inside = False
    col_iter = col + col_dir
    row_iter = row + row_dir
    while col_iter >= 0 and col_iter <= 7 and row_iter >= 0 and row_iter <= 7:
        # print("iterating:", col_iter, row_iter)
        if oponent_inside and board[row_iter][col_iter] == player:
            # bingo! fill this direction
            # print("filling dir found! (col/row):", col_dir, row_dir)
            col_fill = col + col_dir
            row_fill = row + row_dir
            while board[row_fill][col_fill] == oponent:
                board[row_fill][col_fill] = player
                col_fill = col_fill + col_dir
                row_fill = row_fill + row_dir
            board[row][col] = player
            # print("dir filled succsfully!")
            break
        elif board[row_iter][col_iter] == oponent:
            oponent_inside = True
        col_iter = col_iter + col_dir
        row_iter = row_iter + row_dir
    return board


def set_oponent(player):
    if player == 1:
        return 2
    else:
        return 1


def is_legal_move(board, player, move):
    # print(f"Player: {player}, move: {move} is legal?")
    row, col = move
    if not board[row][col] == 0:
        return False

    oponent = set_oponent(player)

    # try west, east, nort, sout, northwest, ...
    col_row_dir = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (1, 1), (-1, 1)]
    for col_row in col_row_dir:
        col_dir, row_dir = col_row
        if check_dir(board, player, oponent, row, col, row_dir, col_dir):
            # print(f"Legal move.")
            return True
    # print(f"Illegal move.")
    return False


def make_move(board, player, move):
    # print(f"Player: {player}, makes move: {move}")
    row, col = move

    oponent = set_oponent(player)

    # try west, east, nort, sout, northwest, ...
    col_row_dir = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (1, 1), (-1, 1)]

    for col_row in col_row_dir:
        col_dir, row_dir = col_row
        # print("filling dir... ", col_row)
        board = fill_dir(board, player, oponent, row, col, row_dir, col_dir)

    return board


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


# return one list of links (and if they are disabled) for the base html navbar
def make_difficulties():
    options = difficulty_options.keys()
    disabled = [difficulty_options[key]["disabled"] for key in options]
    return zip(disabled, options)


def print_board(board):
    for line in board:
        print(line)


def build_end_message(scores):
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


#####################
### DB operations ###
#####################

def save_gamestate(board, game_id):
    flat_board = [item for row in board for item in row]
    board_string = ""
    for num in flat_board:
        board_string += str(num)
    print(board_string)
    gameDB_object = GameDB.objects.get(pk=game_id)
    game_state_entry = GameState(game_id=gameDB_object, board=board_string)
    game_state_entry.save()


def save_game(game_id, score_p1, score_p2, end):
    gameDB_object = GameDB.objects.get(pk=game_id)
    gameDB_object.game_over = end
    gameDB_object.score_p1 = score_p1
    gameDB_object.score_p2 = score_p2
    gameDB_object.save()
    return True


def removegame_db(game_id, user):
    gameDB_object = GameDB.objects.get(pk=game_id)
    if gameDB_object.user == user:
        gameDB_object.delete()
        return True
    else:
        return False


##################################
### machine player definitions ###
##################################

def random_machine_move(board, player):
    print("random move ...")
    possible_moves = get_possible_moves(board, player)
    l = len(possible_moves)
    return possible_moves[random.randint(0, l - 1)]


def greedy_machine_move(board, player, possible_moves=None):
    print("greedy move ...")
    if not possible_moves:
        possible_moves = get_possible_moves(board, player)
    # print("Possible moves: ", possible_moves)
    top_move_score = 0
    top_move = 0
    for move in possible_moves:
        new_board = make_move(copy.deepcopy(board), player, move)
        score_p1, score_p2 = get_scores(new_board)
        if player == 1:
            move_score = score_p1
        else:
            move_score = score_p2
        if move_score > top_move_score:
            top_move = move
    return top_move


def greedy_machine_move_plus(board, player):
    print("greedy plus move ...")
    power_spots = [(0, 0), (0, 7), (7, 0), (7, 7), (0, 2), (0, 5), (7, 2), (7, 5), (5, 7), (2, 7), (5, 0), (2, 0)]
    bad_spots = [(0, 1), (0, 6), (1, 7), (6, 7), (7, 6), (7, 1), (6, 0), (1, 0), (1, 1), (1, 6), (6, 6), (6, 1)]
    possible_moves = get_possible_moves(board, player)
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
    move = greedy_machine_move(board, player, possible_moves=better_moves)

    # in case all moves are bad and where elminated
    if not move:
        print("No moves left after bad moves clean up! Regular greedy move.")
        move = greedy_machine_move(board, player)
    # No power moves, just go for greedy
    return move


# dictionary used for navbar and redirection of used method to the game logic loop
difficulty_options = {
    "easy": {"name": "easy", "type": "random", "method": random_machine_move, "disabled": ""},
    "medium": {"name": "medium", "type": "greedy", "method": greedy_machine_move, "disabled": ""},
    "hard": {"name": "hard", "type": "greedy plus", "method": greedy_machine_move_plus, "disabled": ""},
    "harder": {"name": "harder", "type": "alpha-beta", "method": greedy_machine_move_plus, "disabled": "disabled"},
}


####################
### DJANGO VIEWS ###
####################

# default view which renders an animation
def index(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = False

    return render(request, "index.html", {"user": user, "difficulties": make_difficulties()})


# game board initialization
def newgame(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return render(request, "users/login.html", {"message": "Please login first to start a new game!", "user": False,
                                                    "difficulties": make_difficulties()})

    difficulty = request.GET["difficulty"]

    newgame = Game()
    # Test boards
    # newgame = TestGameP1LastMoveToDraw()
    # newgame = TestGameP1LastMoveToWin()
    # newgame = TestGameP1LastMoveToLose()
    # newgame = TestGameP1MoveP2LastMoveToWin()
    # newgame = TestGameP1MoveP2LastMoveToLose()

    newgame.machine_type = difficulty

    print("NEW GAME STARTED! Difficulty: ", difficulty)
    print_board(newgame.board)

    # save game state variables to session variables
    request.session['board'] = newgame.board
    request.session['human_player'] = newgame.human_player
    request.session['machine_type'] = newgame.machine_type

    # save game to DB
    game_db_entry = GameDB(user=user, player1="human", player2=newgame.machine_type, game_over=False)
    game_db_entry.save()
    request.session["game_id"] = game_db_entry.id

    # save game to DB
    save_gamestate(newgame.board, game_db_entry.id)

    return HttpResponseRedirect(reverse("reversi"))


# initial game view
def reversi(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    board = request.session['board']
    player = 1
    machine = request.session['machine_type']

    return render(request, "reversi.html", {"user": user, "board": board, "player": player, "machine_type": machine,
                                            "difficulties": make_difficulties(),
                                            "possible_moves": get_possible_moves(board, player)})


# Main Game Logic is executed in this view every time Player1 makes a move via browser input
# returns a json data object to browser which updates game board, scores and infos with JS
@method_decorator(csrf_exempt, name='dispatch')
def move(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        row = int(request.POST["row"])
        col = int(request.POST["col"])
        move = (row, col)

        board = request.session['board']
        machine_type = request.session['machine_type']
        game_id = request.session['game_id']
        player = 1
        oponent = set_oponent(player)
        machine_move = None

        # no real move, just querying board status
        if move == (-1, -1):
            message = f""
            scores = get_scores(board)
            data = {"board": board, "message": {"message": message, "color": "white"}, "player": player,
                    "scores": scores, "possible_moves": get_possible_moves(board, player)}
            return JsonResponse(data, safe=False)

        # make a real move
        else:
            if is_legal_move(board, player, move):
                # human players move
                print("")
                print("### HUMAN PLAYER ###")
                print("Possible moves: ", get_possible_moves(board, player))

                # make move and save board
                board = make_move(board, player, move)

                request.session['board'] = board
                print("New board state:")
                print_board(board)

                # switch to machine players after move is made
                print("### MACHINE PLAYER ###")
                print("Possible moves: ", get_possible_moves(board, oponent))

                # is able to move?
                if len(get_possible_moves(board, oponent)) > 0:
                    try:
                        machine_move = difficulty_options[machine_type]["method"](board, oponent)
                    except KeyError:
                        print("ERROR: wrong machine player!")
                    board = make_move(board, oponent, machine_move)
                    print(f"AI ({machine_type}) MOVE: {machine_move}")
                else:
                    print("AI can't move")

                # is game over?
                while len(get_possible_moves(board, player)) == 0:
                    print("Human can't move")
                    if len(get_possible_moves(board, oponent)) == 0:
                        print("AI can't move either. Game Over!")
                        scores = get_scores(board)

                        # save to DB:
                        save_game(game_id, scores[0], scores[1], True)

                        message, winning_player = build_end_message(scores)

                        data = {"board": board, "message": {"message": message, "color": "orange"},
                                "player": winning_player, "scores": scores, "game_over": True}
                        return JsonResponse(data, safe=False)
                    else:
                        print("Human has to pass. Machine moves...")
                        try:
                            machine_move = difficulty_options[machine_type]["method"](board, oponent)
                        except KeyError:
                            print("ERROR: wrong machine player!")
                        board = make_move(board, oponent, machine_move)
                        print(f"AI ({machine_type}) MOVE: {machine_move}")

                scores = get_scores(board)

                # save gamestate to DB and session
                save_game(game_id, scores[0], scores[1], False)
                save_gamestate(board, request.session["game_id"])
                request.session['board'] = board

                # return new board state to browser
                if not machine_move:
                    message = f"opponent had to pass!"
                    color = "orange"
                else:
                    r, c = machine_move
                    message = f"opponent move: row {r + 1}, col {c + 1}"
                    color = "white"

                # return data
                data = {"board": board, "message": {"message": message, "color": color}, "player": player,
                        "scores": scores, "possible_moves": get_possible_moves(board, player)}
                return JsonResponse(data, safe=False)

            # not a legal move
            else:
                message = f"illegal move!"
                scores = get_scores(board)
                data = {"board": board, "message": {"message": message, "color": "red"}, "player": player,
                        "scores": scores, "possible_moves": get_possible_moves(board, player)}
                return JsonResponse(data, safe=False)


def loadgame(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = False

    game_id = int(request.GET["game_id"])
    request.session['game_id'] = game_id
    print("Game ID: ", game_id)

    gameDB_object = GameDB.objects.get(pk=game_id)
    print("Game object: ", gameDB_object)

    # game_state_objects = GameState.objects.all().filter(game_id=gameDB_object)[::-1]
    # game_state = game_state_objects[0]
    game_state = GameState.objects.all().filter(game_id=gameDB_object).last()
    print("Got GameState object from DB:", game_state)

    # deserialize board and save it to session variable
    board_string = game_state.board
    print(board_string)
    game_board = [[0, 0, 0, 0, 0, 0, 0, 0] for x in range(8)]

    cell = 0
    for r in range(8):
        for c in range(8):
            game_board[r][c] = int(board_string[cell])
            cell += 1

    print("Game Board loaded!")
    print_board(game_board)

    # save game state variables to session variables
    request.session['board'] = game_board
    request.session['human_player'] = gameDB_object.player1
    request.session['machine_type'] = gameDB_object.player2

    return HttpResponseRedirect(reverse("reversi"))


# return a list o saved games for the current user
def savedgames(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = False

    saved_games = reversed(GameDB.objects.all().filter(user=user)[:100])

    return render(request, "savedgames.html",
                  {"user": user, "difficulties": make_difficulties(), "saved_games": saved_games})


def deletegame(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = False

    game_id = request.GET["game_id"]

    if removegame_db(game_id, user):
        print(f"Game with id #{game_id} deleted!")
    else:
        print(f"Error deleting game with id #{game_id}")

    return HttpResponseRedirect(reverse("savedgames"))


def login_view(request):
    if request.method == "GET":
        return render(request, "users/login.html",
                      {"message": "Please enter your username and password.", "user": False,
                       "difficulties": make_difficulties()})
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "users/login.html",
                      {"message": "Invalid credentials.", "user": False, "difficulties": make_difficulties()})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "GET":
        return render(request, "users/register.html",
                      {"message": "Please choose a username and password to register a new player.", "user": False,
                       "difficulties": make_difficulties()})

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if len(User.objects.all().filter(username=username)) > 0:
            return render(request, "users/register.html", {"message": "Username already in use.", "user": False})
        else:
            new_user = User.objects.create_user(username=username, password=password)
            new_user.save()
            print("User created:", username, password)

            user = authenticate(request, username=username, password=password)
            login(request, user)
            # print(user)
            return HttpResponseRedirect(reverse("index"))
