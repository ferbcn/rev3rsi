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
difficulties = [('', 'easy'), ('', 'hard'), ('', 'harder'), ('disabled', 'hardest')]
difficulties_extra = [('', 'easy'), ('', 'hard'), ('', 'harder'), ('disabled', 'draw')]


# default view which renders an animation
def index(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_superuser == True:
            return render(request, "index.html", {"user": user, "difficulties": difficulties_extra})
    else:
        user = False

    return render(request, "index.html", {"user": user, "difficulties": difficulties})


# initial game view
def reversi(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    # Restore Gamestate from DB
    game_id = request.session['game_id']
    board, player1, player2 = load_gamestate_db(game_id, user)

    # Something went wrong retrieving board (db error or cheating)
    if board is None:
        return render(request, "index.html", {"user": user, "difficulties": difficulties})

    difficulty = request.session['game_level']
    game = Game(player1, player2, difficulty, board=board)

    return render(request, "reversi.html", {"user": user, "board": game.board, "player": player1, "game_level": difficulty,
                                            "difficulties": difficulties,
                                            "possible_moves": game.get_possible_moves(board, player1)})


# game board initialization
def newgame(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return render(request, "users/login.html", {"message": "Please login first to start a new game!", "user": False,
                                                    "difficulties": difficulties})

    # Game level is passed as url parameter http://localhost/newgame?difficulty=...
    difficulty = request.GET["difficulty"]
    # Define game parameters
    # p1 == 1 and p2 == 2 --> p1 is green and p2 is blue, green always starts
    player1 = "human"
    player2 = difficulty

    # Test boards
    # new_game = TestGameP1LastMoveToDraw(player1, player2, difficulty)
    # new_game = TestGameP1LastMoveToLose(player1, player2, difficulty)
    # new_game = TestGameP1MoveP2LastMoveToWin(player1, player2, difficulty)
    # new_game = TestGameP1MoveP2LastMoveToLose(player1, player2, difficulty)
    # new_game = TestGameP1LastMoveToWin(player1, player2, difficulty)

    # New Game and board initialization
    new_game = Game(player1, player2, difficulty, board=None)
    print("NEW GAME STARTED! Difficulty: ", difficulty)
    for line in new_game.board: print(line)

    # save game state variables to session variables
    request.session['board'] = new_game.board
    request.session['human_player'] = 1
    request.session['player1'] = 1
    request.session['player2'] = 1
    request.session['game_level'] = new_game.difficulty

    # save game to DB
    game_db_entry = GameDB(user=user, player1=player1, player2=player2, game_over=False)
    game_db_entry.save()
    request.session["game_id"] = game_db_entry.id

    # save game to DB
    save_gamestate_db(new_game.board, game_db_entry.id)

    return HttpResponseRedirect(reverse("reversi"))


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

        # Restore gamestate from DB
        game_id = request.session['game_id']
        board, player1, player2 = load_gamestate_db(game_id, user)
        difficulty = player2

        # Something went wrong retrieving board (db error or cheating)
        if board is None:
            return render(request, "index.html", {"user": user, "difficulties": difficulties})

        game = Game(player1, player2, difficulty, board=board)

        # Define player1 (player) and player2 (opponent)
        player1 = Player()

        # no real move, just querying board status
        if move == (-1, -1):
            message = f""
            scores = game.get_scores(board)
            data = {"board": board, "message": {"message": message, "color": "white"}, "player": player1.player,
                    "scores": scores, "possible_moves": game.get_possible_moves(board, player1.player)}
            return JsonResponse(data, safe=False)

        if difficulty == "easy":
            player2 = AiRandom()
            print("Random Ai initiated")
        elif difficulty == "hard":
            player2 = AiGreedy()
            print("Greedy Ai initiated")
        elif difficulty == "harder":
            player2 = AiGreedyPlus()
            print("Greedy Plus Ai initiated")
        """
        else:
            print("ERROR: wrong machine player! Selecting default level: easy!")
            player2 = AiRandom()
        """

        player2.player = game.get_opponent(player1.player)

        #machine_move = None

        # make a real move
        if game.is_legal_move(board, player1.player, move):
            # player1 move
            print("### PLAYER 1 ###")
            possible_moves = game.get_possible_moves(board, player1.player)
            print(possible_moves)
            print("Player1 MOVE: ", move)

            # make move and save board
            game.board = player1.make_move(board, player1.player, move)

            #print("New board state:")
            #for line in board: print(line)

            # switch to player2 after move is made
            print("### PLAYER 2 ###")
            possible_moves = game.get_possible_moves(game.board, player2.player)
            print(possible_moves)

            # is able to move?
            if len(possible_moves) > 0:
                machine_move = player2.machine_move(game, possible_moves)
                game.board = player2.make_move(board, player2.player, machine_move)
                print(f"Player2 MOVE: {machine_move}")
            else:
                print("Player 2 can't move")

            # is game over?
            while len(game.get_possible_moves(game.board, player1.player)) == 0:
                print("Player1 can't move")
                possible_moves = game.get_possible_moves(game.board, player2.player)
                if len(possible_moves) == 0:
                    print("Player2 can't move either. Game Over!")
                    scores = game.get_scores(board)

                    # save to DB:
                    save_game_db(game_id, scores[0], scores[1], True)
                    message, winning_player = game.build_end_message(scores)

                    # send response:
                    data = {"board": game.board, "message": {"message": message, "color": "orange"},
                            "player": winning_player, "scores": scores, "game_over": True}
                    return JsonResponse(data, safe=False)
                else:
                    machine_move = player2.machine_move(game, possible_moves)
                    board = player2.make_move(board, player2.player, machine_move)
                    print(f"Player2 MOVE: {machine_move}")


            scores = game.get_scores(board)

            # save gamestate to DB and session
            save_game_db(game_id, scores[0], scores[1], False)
            save_gamestate_db(game.board, game_id)
            request.session['board'] = game.board

            # return new board state to browser
            if not machine_move:
                message = f"Player2 pass!"
                color = "orange"
            else:
                r, c = machine_move
                message = f"Player2 move: row {r + 1}, col {c + 1}"
                color = "white"

            # return data
            data = {"board": game.board, "message": {"message": message, "color": color}, "player": player1.player,
                    "scores": scores, "possible_moves": game.get_possible_moves(board, player1.player)}
            return JsonResponse(data, safe=False)

        # not a legal move
        else:
            message = f"illegal move!"
            scores = game.get_scores(board)
            data = {"board": game.board, "message": {"message": message, "color": "red"}, "player": player1.player,
                    "scores": scores, "possible_moves": game.get_possible_moves(board, player1.player)}
            return JsonResponse(data, safe=False)


def loadgame(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    game_id = int(request.GET["game_id"])
    request.session['game_id'] = game_id
    print("Game ID: ", game_id)

    board, player1, player2 = load_gamestate_db(game_id, user)
    # Something went wrong retrieving board (db error or cheating)
    if board is None:
        return render(request, "index.html", {"user": user, "difficulties": difficulties})

    for line in board: print(line)

    # save game state variables to session variables
    request.session['board'] = board
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

    if remove_game_db(game_id, user):
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
