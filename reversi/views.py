from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse

from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# from django.core import serializers
from django.views.decorators.http import require_http_methods

from reversi.test_games import *
from reversi.game_logic import *
from reversi.data_layer import *

# Game difficulties and which are available
from .game_levels import Levels

# default view which renders an animation
def index(request):
    lev = Levels()
    if request.user.is_authenticated:
        user = request.user
        if user.is_superuser:
            levels = lev.get_admin_levels()
        else:
            levels = lev.get_levels()
    else:
        user = False
        levels = lev.get_levels()

    return render(request, "index.html", {"user": user, "game_levels": levels})


# game board initialization (player vs machine)
def newgame(request):
    levels = Levels()
    if request.user.is_authenticated:
        user = request.user
    else:
        level = request.GET["difficulty"]
        return render(request, "users/login.html", {"message": "Please login first to start a new game!", "user": False,
                                                    "game_levels": levels.get_levels(), "level": level})

    # Game level is passed as url parameter http://localhost/newgame?difficulty=...
    difficulty = request.GET["difficulty"]

    # Define random role of players
    human_is_player1 = random.choice([True, False])
    if human_is_player1 == 1:
        player1_name = "human"
        player2_name = difficulty
        request.session["machine_role"] = 2
    else:
        player1_name = difficulty
        player2_name = "human"
        request.session["machine_role"] = 1

    # Launch a test game
    if user.is_superuser:
        if difficulty == "P1-Draw":
            new_game = TestGameP1LastMoveToDraw(player1_name, player2_name, difficulty)
        elif difficulty == "P1-Win":
            new_game = TestGameP1LastMoveToWin(player1_name, player2_name, difficulty)
        elif difficulty == "P1-Lose":
            new_game = TestGameP1LastMoveToLose(player1_name, player2_name, difficulty)
        elif difficulty == "P2-Win":
            new_game = TestGameP1MoveP2LastMoveToWin(player1_name, player2_name, difficulty)
        elif difficulty == "P2-Lose":
            new_game = TestGameP1MoveP2LastMoveToLose(player1_name, player2_name, difficulty)
        elif difficulty == "JumpCheck":
            new_game = TestGameJumpCheck(player1_name, player2_name, difficulty)
        else:
            new_game = Game(player1_name, player2_name, difficulty, board=None)
    else:
        # Launch a real new game
        # New Game and board initialization
        new_game = Game(player1_name, player2_name, difficulty, board=None)

    print("NEW GAME STARTED! Difficulty: ", difficulty)
    for line in new_game.board:
        print(line)

    scores = get_scores(new_game.board)

    # save game to DB
    game_db_entry = GameDB(user=user, score_p1=scores[0], score_p2=scores[1], player1=player1_name, player2=player2_name, next_player=1, game_over=False)
    game_db_entry.save()

    # Save Session variable
    request.session["game_id"] = game_db_entry.id
    prev_state_id = 0
    request.session['prev_state_id'] = prev_state_id

    # save gamestate to DB and session
    save_gamestate_db(new_game.board, game_db_entry.id, prev_state_id)


    return HttpResponseRedirect(reverse("reversi"))


# game board initialization for match (player vs player)
def newmatch(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        level = request.GET["difficulty"]
        levels = Levels()
        return render(request, "users/login.html", {"message": "Please login first to start a new game!", "user": False,
                                                        "game_levels": levels.get_levels(), "level": level})

    p1_name = request.GET["p1"]
    p2_name = request.GET["p2"]
    difficulty = "match"

    # Define random role of players
    p1_is_player1 = random.choice([True, False])

    if p1_is_player1 == 1:
        player1_name = p1_name
        player2_name = p2_name
    else:
        player1_name = p2_name
        player2_name = p1_name

    # Launch a real new game
    # New Game and board initialization
    new_game = Game(player1_name, player2_name, difficulty, board=None)

    print("NEW MATCH STARTED!")
    print(f'Player1: {player1_name} vs Player2: {player2_name}')
    for line in new_game.board:
        print(line)

    # update scores
    scores = get_scores(new_game.board)
    # and save initial gamestate to DB and session
    game_db_entry = GameDB(user=user, score_p1=scores[0], score_p2=scores[1], player1=player1_name, player2=player2_name,
                           next_player=1, game_over=False)
    game_db_entry.save()

    # save game state variables to session variables
    request.session["game_id"] = game_db_entry.id

    # save game to DB
    save_gamestate_db(new_game.board, game_db_entry.id, None)

    json_response = {"game_id": game_db_entry.id}

    return JsonResponse(json_response, safe=False)


# initial game view
def reversi(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    # Restore Gamestate from DB
    game_id = request.session['game_id']

    try:
        board, green_player, blue_player, next_player, state_id = load_gamestate_db(game_id, user)
    # Something went wrong retrieving board (db error or cheating)
    except Exception as e:
        print(e)
        return render(request, "index.html", {"user": user})

    if green_player == "human":
        print("Green Player is human.")
        difficulty = blue_player
        player_color = 'green'
    elif blue_player == "human":
        print("Blue Player is human.")
        difficulty = green_player
        player_color = 'blue'
    else:
        difficulty = "match"
        print(f"Match: Green is {green_player} and Blue is {blue_player}.")

    lev = Levels()
    if user.is_superuser:
        levels = lev.get_admin_levels()
    else:
        levels = lev.get_levels()

    return render(request, "reversi.html", {"user": user,
                                            "board": board,
                                            "player1_name": green_player,
                                            "player2_name": blue_player,
                                            "game_level": difficulty,
                                            "game_levels": levels,
                                            "user_color": player_color,
                                            })


# initial game view
def reversimatch (request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    # Restore Gamestate from DB
    # Read GameId from session variable
    game_id = request.session['game_id']

    try:
        board, green_player, blue_player, next_player, state_id = load_gamestate_db(game_id, user)
    # Something went wrong retrieving board (db error or cheating)
    except Exception as e:
        print(e)
        return render(request, "index.html", {"user": user})

    difficulty = "match"
    print(f"Match: Green is {green_player} and Blue is {blue_player}.")

    levels = Levels()
    game_levels = levels.get_levels()
    user_color = "green" if user.username == green_player else "blue"

    return render(request, "reversimatch.html",
                    {"username": user.username,
                    "board": board,
                    "player1_name": green_player,
                    "player2_name": blue_player,
                    "game_level": difficulty,
                    "game_levels": game_levels,
                    "game_id": game_id,
                    "user_color": user_color
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
        board, player1_name, player2_name, next_player, state_id = load_gamestate_db(game_id, user)

        if player1_name == "human":
            machine_role = 2
        elif player2_name == "human":
            machine_role = 1
        else:
            machine_role = 0

        possible_moves = get_possible_moves(board, next_player)
        message = f"Player{next_player}'s turn"

        print("Next player:", next_player)
        board_color = 'green' if next_player == 1 else 'blue'
        scores = get_scores(board)

        data = {"board": board, "message": {"message": message, "color": board_color},
                "next_player": next_player, "machine_role": machine_role,
                "scores": scores, "possible_moves": possible_moves, "board_color": board_color}
        return JsonResponse(data, safe=False)


# Main Game Logic is executed in this view every time the current Player makes a move via browser input
# returns a json data object to browser which updates game board, scores and infos with JS
@method_decorator(csrf_exempt, name='dispatch')
@require_http_methods(["POST"])
def move(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    row = int(request.POST["row"])
    col = int(request.POST["col"])
    current_move = (row, col)

    # Restore gamestate from DB
    game_id = request.session['game_id']
    board, player1_name, player2_name, next_player, state_id = load_gamestate_db(game_id, user)

    game_over = False

    # Something went wrong retrieving board (db error or cheating)
    levels = Levels()
    if board is None:
        return render(request, "index.html", {"user": user, "game_levels": levels.get_levels()})

    if player1_name == "human":
        difficulty = player2_name
        human_role = 1
        machine_role = 2
        human_color = 'green'
        machine_color = 'blue'
    elif player2_name == "human":
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
    elif difficulty == "medium":
        machine_player = AiGreedy(role=machine_role)
        print("Greedy Ai initiated")
    elif difficulty == "hard":
        machine_player = AiGreedyPlus(role=machine_role)
        print("Greedy Plus Ai initiated")
    elif difficulty == "harder":
        machine_player = AiMiniMax(role=machine_role)
        print("Greedy Minimax Ai initiated")
    else:
        machine_player = AiMiniMax(role=machine_role)
        print("Greedy Minimax Ai initiated")
        #machine_player = AiGreedy(role=machine_role)
        #print("Defaulting to Greedy Ai")

    message = f""
    color = 'darkgrey'

    if next_player == human_player.role:
        print("### Human Player possible moves:")
    else:
        print("### Machine Player possible moves:")
    possible_moves = get_possible_moves(board, next_player)
    print(possible_moves)

    if next_player == human_player.role:
        print(f"Human move: {move}")
        if is_legal_move(board, human_player.role, current_move):
            next_move, board = human_move(board, human_player, current_move)
            r, c = next_move
            message = f"Human move: row {r + 1}, col {c + 1}"
            color = human_color
            # switch to human player
            next_player = machine_player.role
        else:
            print("Illegal move!!!")
            message = f"Illegal move!"
            color = 'red'
            # do nothing with board
        # Check for Game Over
        if len(get_possible_moves(board, next_player)) == 0:
            next_player = get_opponent(next_player)
            if len(get_possible_moves(board, next_player)) == 0:
                game_over = True

    elif next_player == machine_player.role:
        print("Machine move...")
        # Game Over?
        if len(get_possible_moves(board, next_player)) > 0:
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

    if not game_over:
        save_gamestate_db(board, game_id, state_id)

    request.session['prev_state_id'] = state_id

    data = {"board": board, "message": {"message": message, "color": color},
            "machine_role": machine_player.role, "next_player": next_player, "game_over": game_over,
            "scores": scores, "possible_moves": get_possible_moves(board, next_player)}

    return JsonResponse(data, safe=False)


# Main Game Logic is executed in this view every time the current Player makes a move via browser input
# returns a json data object to browser which updates game board, scores and infos with JS
@method_decorator(csrf_exempt, name='dispatch')
@require_http_methods(["POST"])
def movematch(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    row = int(request.POST["row"])
    col = int(request.POST["col"])
    current_move = (row, col)

    # Restore gamestate from DB
    game_id = request.session['game_id']

    board, player1_name, player2_name, next_player, state_id = load_gamestate_db(game_id, user)

    if next_player == 1:
        next_player_name = player1_name
    else:
        next_player_name = player2_name

    game_over = False

    if user.username == next_player_name:
        levels = Levels()
        # Something went wrong retrieving board (db error or cheating)
        if board is None:
            return render(request, "index.html", {"user": user, "game_levels": levels.get_levels()})

        # Define player1 (player) and player2 (opponent)
        human_player = Player(role=next_player)

        if is_legal_move(board, next_player, current_move):
            next_move, board = human_move(board, human_player, current_move)
            r, c = next_move
            message = f"Player{next_player} move: row {r + 1}, col {c + 1}"
            color = 'lightgrey'
            # switch to human player
            next_player = get_opponent(next_player)
        else:
            #print("Illegal move!!!")
            message = f"Illegal move!"
            color = 'red'
            # do nothing with board

        # Check for Game Over
        if len(get_possible_moves(board, next_player)) == 0:
            next_player = get_opponent(next_player)
            if len(get_possible_moves(board, next_player)) == 0:
                game_over = True

        scores = get_scores(board)
        # save gamestate to DB and session
        save_game_db(game_id, scores[0], scores[1], next_player, game_over)
        if not game_over:
            save_gamestate_db(board, game_id, None)

    # Not your turn!
    else:
        #print(f'Not your turn {user.username}')
        scores = get_scores(board)
        message = f"Not your turn!"
        color = 'red'

    board_color = 'green' if next_player == 1 else 'blue'

    data = {"board": board, "message": {"message": message, "color": color},
            "next_player": next_player, "game_over": game_over,
            "scores": scores, "possible_moves": get_possible_moves(board, next_player), "board_color": board_color}

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

    try:
        board, player1, player2, next_player, state_id = load_gamestate_db(game_id, user)
    # Something went wrong retrieving board (db error or cheating)
    except Exception as e:
        print(f"DB Error: {e}")
        levels = Levels()
        return render(request, "index.html", {"user": user, "game_levels": levels.get_levels()})

    for line in board: print(line)

    if "human" in [player1, player2]:
        return HttpResponseRedirect(reverse("reversi"))
    else:
        return HttpResponseRedirect(reverse("reversimatch"))

def load_prev_gamestate(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    game_id = request.session['game_id']
    print("Game ID: ", game_id)

    try:
        board, player1, player2, next_player, state_id = load_gamestate_db(game_id, user, prev=1)
    # Something went wrong retrieving board (db error or cheating)
    except Exception as e:
        print(f"DB Error: {e}")
        levels = Levels()
        return render(request, "index.html", {"user": user, "game_levels": levels.get_levels()})

    for line in board: print(line)

    if "human" in [player1, player2]:
        return HttpResponseRedirect(reverse("reversi"))
    else:
        return HttpResponseRedirect(reverse("reversimatch"))

# return a list o saved games for the current user
def savedgames(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    saved_games = get_saved_games_for_user(user)

    levels = Levels()
    if user.is_superuser:
        levels = levels.get_admin_levels()
    else:
        levels = levels.get_levels()

    return render(request, "savedgames.html",
                  {"user": user, "game_levels": levels, "saved_games": saved_games})


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
        levels = Levels()
        return render(request, "users/login.html",
                      {"message": "Please enter your username and password.", "user": False,
                       "game_levels": levels.get_levels()})

    username = request.POST["username"]
    password = request.POST["password"]
    redirect = request.POST["redirect"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # if user selects level and is not logged in he is redirected to login page,
        # where a hidden value is saved in the form and send together with login data
        # in order to redirect the user after a successful login... hacky? yes, sir!
        if len(redirect) > 0:
            redirect = "newgame?difficulty=" + redirect
            return HttpResponseRedirect(redirect)
        return HttpResponseRedirect(reverse("index"))
    else:
        levels = Levels()
        return render(request, "users/login.html",
                      {"message": "Invalid credentials.", "user": False, "game_levels": levels.get_levels()})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    levels = Levels()
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "GET":
        return render(request, "users/register.html",
                      {"message": "Please choose a username and password.", "user": False,
                       "game_levels": levels.get_levels()})

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if len(User.objects.all().filter(username=username)) > 0:
            return render(request, "users/register.html", {"message": "Username already in use!", "user": False})
        elif len(username) < 3:
            return render(request, "users/register.html", {"message": "Username too short!", "user": False})
        elif len(password) < 3:
            return render(request, "users/register.html", {"message": "Password too short!", "user": False})
        else:
            new_user = User.objects.create_user(username=username, password=password)
            new_user.save()
            print("User created:", username, password)

            user = authenticate(request, username=username, password=password)
            login(request, user)
            # print(user)
            return HttpResponseRedirect(reverse("index"))
