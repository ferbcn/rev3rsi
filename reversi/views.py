from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse

from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# from django.core import serializers

from .models import GameDB, GameState

from reversi.test_games import *
from reversi.reversi_game import Game


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


####################
### DJANGO VIEWS ###
####################

# Game difficulties and which of thema are available
# Hardest Level is disabled by default
difficulties = [((), 'easy'), ((), 'hard'), ((), 'harder'), ('disabled', 'hardest')]

# default view which renders an animation
def index(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = False

    return render(request, "index.html", {"user": user, "difficulties": difficulties})


# game board initialization
def newgame(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return render(request, "users/login.html", {"message": "Please login first to start a new game!", "user": False,
                                                    "difficulties": difficulties})

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
    for line in newgame.board: print(line)

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

    game = Game(board)

    return render(request, "reversi.html", {"user": user, "board": board, "player": player, "machine_type": machine,
                                            "difficulties": difficulties,
                                            "possible_moves": game.get_possible_moves(board, player)})


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

        game = Game(board)

        machine_type = request.session['machine_type']
        game_id = request.session['game_id']
        player = 1
        oponent = game.set_oponent(player)
        machine_move = None

        # no real move, just querying board status
        if move == (-1, -1):
            message = f""
            scores = game.get_scores(board)
            data = {"board": board, "message": {"message": message, "color": "white"}, "player": player,
                    "scores": scores, "possible_moves": game.get_possible_moves(board, player)}
            return JsonResponse(data, safe=False)

        # make a real move
        else:
            if game.is_legal_move(board, player, move):
                # human players move
                print("")
                print("### HUMAN PLAYER ###")
                print("Possible moves: ", game.get_possible_moves(board, player))

                # make move and save board
                board = game.make_move(board, player, move)

                request.session['board'] = board
                print("New board state:")
                for line in board: print(line)

                # switch to machine players after move is made
                print("### MACHINE PLAYER ###")
                print("Possible moves: ", game.get_possible_moves(board, oponent))

                # is able to move?
                if len(game.get_possible_moves(board, oponent)) > 0:
                    try:
                        machine_move = game.difficulty_options[machine_type]["method"](board, oponent)
                    except KeyError:
                        print("ERROR: wrong machine player!")
                    board = game.make_move(board, oponent, machine_move)
                    print(f"AI ({machine_type}) MOVE: {machine_move}")
                else:
                    print("AI can't move")

                # is game over?
                while len(game.get_possible_moves(board, player)) == 0:
                    print("Human can't move")
                    if len(game.get_possible_moves(board, oponent)) == 0:
                        print("AI can't move either. Game Over!")
                        scores = game.get_scores(board)

                        # save to DB:
                        save_game(game_id, scores[0], scores[1], True)

                        message, winning_player = game.build_end_message(scores)

                        data = {"board": board, "message": {"message": message, "color": "orange"},
                                "player": winning_player, "scores": scores, "game_over": True}
                        return JsonResponse(data, safe=False)
                    else:
                        print("Human has to pass. Machine moves...")
                        try:
                            machine_move = game.difficulty_options[machine_type]["method"](board, oponent)
                        except KeyError:
                            print("ERROR: wrong machine player!")
                        board = game.make_move(board, oponent, machine_move)
                        print(f"AI ({machine_type}) MOVE: {machine_move}")

                scores = game.get_scores(board)

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
                        "scores": scores, "possible_moves": game.get_possible_moves(board, player)}
                return JsonResponse(data, safe=False)

            # not a legal move
            else:
                message = f"illegal move!"
                scores = game.get_scores(board)
                data = {"board": board, "message": {"message": message, "color": "red"}, "player": player,
                        "scores": scores, "possible_moves": game.get_possible_moves(board, player)}
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

    for line in game_board: print(line)

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
                  {"user": user, "difficulties": difficulties, "saved_games": saved_games})


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
                       "difficulties": difficulties})
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "users/login.html",
                      {"message": "Invalid credentials.", "user": False, "difficulties": difficulties})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "GET":
        return render(request, "users/register.html",
                      {"message": "Please choose a username and password to register a new player.", "user": False,
                       "difficulties": difficulties})

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
