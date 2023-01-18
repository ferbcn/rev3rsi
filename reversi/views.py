from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse

from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# from django.core import serializers

from reversi.test_games import *
from reversi.reversi_game import *
from reversi.db_operations_orm import *


# Game difficulties and which are available
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

    # Test boards
    # new_game = TestGameP1LastMoveToDraw()
    # new_game = TestGameP1LastMoveToWin()
    # new_game = TestGameP1LastMoveToLose()
    # new_game = TestGameP1MoveP2LastMoveToWin()
    # new_game = TestGameP1MoveP2LastMoveToLose()

    # Game level is passed as url parameter http://localhost/newgame?difficulty=...
    difficulty = request.GET["difficulty"]
    # Define game parameters
    # p1 == 1 and p2 == 2 --> p1 is green and p2 is blue, green always starts
    player1 = "human"
    player2 = difficulty
    new_game = Game(player1, player2, difficulty)

    print("NEW GAME STARTED! Difficulty: ", difficulty)
    for line in new_game.board: print(line)

    # save game state variables to session variables
    request.session['board'] = new_game.board
    request.session['human_player'] = new_game.current_player
    request.session['game_level'] = new_game.difficulty

    # save game to DB
    game_db_entry = GameDB(user=user, player1=player1, player2=player2, game_over=False)
    game_db_entry.save()
    request.session["game_id"] = game_db_entry.id

    # save game to DB
    save_gamestate(new_game.board, game_db_entry.id)

    return HttpResponseRedirect(reverse("reversi"))


# initial game view
def reversi(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    # Restore Gamestate from DB
    game_id = request.session['game_id']
    board, player1, player2 = load_gamestate(game_id)

    difficulty = request.session['game_level']

    game = Game(player1, player2, difficulty, board=board)

    return render(request, "reversi.html", {"user": user, "board": board, "player": player1, "game_level": difficulty,
                                            "difficulties": difficulties,
                                            "possible_moves": game.get_possible_moves(board, player1)})


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

        difficulty = request.session['game_level']
        game_id = request.session['game_id']

        human = Player()

        machine_move = None

        # Restore Gamestate from DB
        game_id = request.session['game_id']
        board, player1, player2 = load_gamestate(game_id)

        difficulty = player2

        game = Game(player1, player2, difficulty, board=board)

        opponent = game.get_opponent(human.player)

        # no real move, just querying board status
        if move == (-1, -1):
            message = f""
            scores = game.get_scores(board)
            data = {"board": board, "message": {"message": message, "color": "white"}, "player": human.player,
                    "scores": scores, "possible_moves": game.get_possible_moves(board, human.player)}
            return JsonResponse(data, safe=False)

        # make a real move
        else:
            if game.is_legal_move(board, human.player, move):
                # human players move
                print("")
                print("### HUMAN PLAYER ###")
                print("Possible moves: ", game.get_possible_moves(board, human.player))

                # make move and save board
                board = human.make_move(board, human.player, move)

                request.session['board'] = board
                print("New board state:")
                for line in board: print(line)

                # switch to machine players after move is made
                possible_moves = game.get_possible_moves(board, opponent)
                print("### MACHINE PLAYER ###")
                print("Possible moves: ", possible_moves)

                # is able to move?
                if len(possible_moves) > 0:
                    if difficulty == "easy":
                        ai = AiRandom()
                    elif difficulty == "hard":
                        ai = AiGreedy()
                    elif difficulty == "harder":
                        ai = AiGreedyPlus()
                    else:
                        print("ERROR: wrong machine player!")
                    machine_move = ai.machine_move(game, possible_moves)
                    board = ai.make_move(board, opponent, machine_move)
                    print(f"AI ({difficulty}) MOVE: {machine_move}")
                else:
                    print("AI can't move")

                # is game over?
                while len(game.get_possible_moves(board, human.player)) == 0:
                    print("Human can't move")
                    if len(game.get_possible_moves(board, opponent)) == 0:
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
                            machine_move = game.difficulty_options[difficulty]["method"](board, opponent)
                        except KeyError:
                            print("ERROR: wrong machine player!")
                        board = game.make_move(board, opponent, machine_move)
                        print(f"AI ({difficulty}) MOVE: {machine_move}")

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
                data = {"board": board, "message": {"message": message, "color": color}, "player": human.player,
                        "scores": scores, "possible_moves": game.get_possible_moves(board, human.player)}
                return JsonResponse(data, safe=False)

            # not a legal move
            else:
                message = f"illegal move!"
                scores = game.get_scores(board)
                data = {"board": board, "message": {"message": message, "color": "red"}, "player": human.player,
                        "scores": scores, "possible_moves": game.get_possible_moves(board, human.player)}
                return JsonResponse(data, safe=False)


def loadgame(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    game_id = int(request.GET["game_id"])
    request.session['game_id'] = game_id
    print("Game ID: ", game_id)

    game_board, player1, player2 = load_gamestate(game_id)

    for line in game_board: print(line)

    # save game state variables to session variables
    request.session['board'] = game_board
    request.session['human_player'] = player1
    request.session['game_level'] = player2

    return HttpResponseRedirect(reverse("reversi"))


# return a list o saved games for the current user
def savedgames(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    saved_games = reversed(GameDB.objects.all().filter(user=user)[:100])

    return render(request, "savedgames.html",
                  {"user": user, "difficulties": difficulties, "saved_games": saved_games})


def deletegame(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

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
