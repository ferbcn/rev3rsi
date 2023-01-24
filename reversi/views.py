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
difficulties_admin = [('', 'easy'), ('', 'hard'), ('', 'harder'), ('disabled', 'draw')]


# default view which renders an animation
def index(request):
    if request.user.is_authenticated:
        user = request.user
        if user.is_superuser == True:
            return render(request, "index.html", {"user": user, "difficulties": difficulties_admin})
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

    # Game level is passed as url parameter http://localhost/newgame?difficulty=...
    difficulty = request.GET["difficulty"]
    # Define game parameters
    # p1 == 1 and p2 == 2 --> p1 is green and p2 is blue, green always starts

    human_is_player1 = random.choice([True, False])

    if human_is_player1 == 1:
        player1_name = "human"
        player2_name = difficulty
        human_role = 1
    else:
        player1_name = difficulty
        player2_name = "human"
        human_role = 2
    # Test boards
    # new_game = TestGameP1LastMoveToDraw(player1, player2, difficulty)
    # new_game = TestGameP1LastMoveToLose(player1, player2, difficulty)
    # new_game = TestGameP1MoveP2LastMoveToWin(player1, player2, difficulty)
    # new_game = TestGameP1MoveP2LastMoveToLose(player1, player2, difficulty)
    # new_game = TestGameP1LastMoveToWin(player1, player2, difficulty)

    # New Game and board initialization
    new_game = Game(player1_name, player2_name, difficulty, board=None)
    print("NEW GAME STARTED! Difficulty: ", difficulty)
    for line in new_game.board:
        print(line)

    # save game state variables to session variables
    request.session['board'] = new_game.board
    request.session['human_player'] = human_role
    request.session['game_level'] = new_game.difficulty

    # save game to DB
    game_db_entry = GameDB(user=user, player1=player1_name, player2=player2_name, next_player=1, game_over=False)
    game_db_entry.save()
    request.session["game_id"] = game_db_entry.id

    # save game to DB
    save_gamestate_db(new_game.board, game_db_entry.id)

    return HttpResponseRedirect(reverse("reversi"))



# initial game view
def reversi(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    # Restore Gamestate from DB
    game_id = request.session['game_id']
    try:
        board, player1, player2, next_player = load_gamestate_db(game_id, user)
    # Something went wrong retrieving board (db error or cheating)
    except Exception as e:
        print(e)
        return render(request, "index.html", {"user": user, "difficulties": difficulties})

    if player1 == "human":
        print("P1 is human.")
        difficulty = player2
        player2 = "Machine"
    else:
        print("P2 is human.")
        difficulty = player1
        player1 = "Machine"

    return render(request, "reversi.html", {"user": user,
                                            "board": board,
                                            "player1_name": player1.capitalize(),
                                            "player2_name": player2.capitalize(),
                                            "game_level": difficulty,
                                            "difficulties": difficulties,
                                            })


# Query board status
@method_decorator(csrf_exempt, name='dispatch')
def queryboard(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "GET":
        # Restore gamestate from DB
        game_id = request.session['game_id']
        board, player1_name, player2_name, next_player = load_gamestate_db(game_id, user)

        if player1_name == "human":
            machine_role = 2
        else:
            machine_role = 1

        possible_moves = get_possible_moves(board, next_player)
        message = f"Player{next_player}'s turn"
        scores = get_scores(board)

        data = {"board": board, "message": {"message": message, "color": "white"},
                "machine_role": machine_role, "next_player": next_player, "game_over": False,
                "scores": scores, "possible_moves": possible_moves}
        return JsonResponse(data, safe=False)


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
        board, player1_name, player2_name, next_player = load_gamestate_db(game_id, user)

        game_over = False

        # Something went wrong retrieving board (db error or cheating)
        if board is None:
            return render(request, "index.html", {"user": user, "difficulties": difficulties})

        if player1_name == "human":
            difficulty = player2_name
            human_role = 1
            machine_role = 2
            human_color = 'green'
            machine_color = 'blue'
        else:
            difficulty = player1_name
            human_role = 2
            machine_role = 1
            human_color = 'blue'
            machine_color = 'green'

        # Define player1 (player) and player2 (opponent)
        human_player = Player(role=human_role)

        if difficulty == "easy":
            machine_player = AiRandom(role=machine_role)
            print("Random Ai initiated")
        elif difficulty == "hard":
            machine_player = AiGreedy(role=machine_role)
            print("Greedy Ai initiated")
        elif difficulty == "harder":
            machine_player = AiGreedyPlus(role=machine_role)
            print("Greedy Plus Ai initiated")

        message = f""
        color = 'white'

        if next_player == human_player.role:
            print("### Human Player possible moves:")
        else:
            print("### Machine Player possible moves:")
        possible_moves = get_possible_moves(board, next_player)
        print(possible_moves)

        if next_player == human_player.role:
            print(f"Human move: {move}")
            if is_legal_move(board, human_player.role, move):
                next_move, board = human_move(board, human_player, move)
                r, c = next_move
                message = f"Human move: row {r + 1}, col {c + 1}"
                color = human_color
                # switch to human player
                next_player = machine_player.role
                # Check for Game Over
                if len(get_possible_moves(board, next_player)) == 0:
                    if len(get_possible_moves(board, get_opponent(next_player))) == 0:
                        game_over = True
            else:
                print("Illegal move!!!")
                message = f"Illegal move!"
                color = 'red'
                # do nothing with board

        elif next_player == machine_player.role:
            print("Machine move...")
            next_move, board = machine_move(board, machine_player)
            r, c = next_move
            message = f"Machine move: row {r + 1}, col {c + 1}"
            color = machine_color
            if next_move is None:
                print("Machine can't move...")
                message = f"AI can't move!"
            # switch to human player
            next_player = human_player.role
            # Check for Game Over
            if len(get_possible_moves(board, next_player)) == 0:
                if len(get_possible_moves(board, get_opponent(next_player))) == 0:
                    game_over = True

        scores = get_scores(board)
        # save gamestate to DB and session
        save_game_db(game_id, scores[0], scores[1], next_player, game_over)
        save_gamestate_db(board, game_id)

        data = {"board": board, "message": {"message": message, "color": color},
                "machine_role": machine_player.role, "next_player": next_player, "game_over": game_over,
                "scores": scores, "possible_moves": get_possible_moves(board, next_player)}

        return JsonResponse(data, safe=False)



def human_move(board, human_player, move):
    # make a human move
    print("Human move: ", move)
    # make move and save board
    board = human_player.make_move(board, human_player.role, move)
    return move, board


def machine_move(board, machine_player):
    # make a machine move
    print("### Machine Player ###")
    possible_moves = get_possible_moves(board, machine_player.role)
    print(possible_moves)
    next_move = machine_player.next_move(board, possible_moves)
    print("Machine move: ", next_move)
    board = machine_player.make_move(board, machine_player.role, next_move)
    return next_move, board


def loadgame(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    game_id = int(request.GET["game_id"])
    request.session['game_id'] = game_id
    print("Game ID: ", game_id)

    board, player1, player2, next_game = load_gamestate_db(game_id, user)
    # Something went wrong retrieving board (db error or cheating)
    if board is None:
        return render(request, "index.html", {"user": user, "difficulties": difficulties})

    for line in board: print(line)

    # save game state variables to session variables
    request.session['board'] = board
    request.session['player1_name'] = player1
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
