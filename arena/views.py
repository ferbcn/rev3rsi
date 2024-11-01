# arena/views.py
import random

from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache

from reversi.data_layer import load_gamestate_db, save_gamestate_db, save_game_db
from reversi.game_levels import Levels
from reversi.game_logic import Game, get_scores, get_possible_moves, Player, is_legal_move, get_opponent, human_move
from reversi.models import GameDB

# Create an instance of the Levels class
levels_maker = Levels()
user_levels = levels_maker.get_levels()


@require_http_methods(["GET"])
def arena_index(request):
    if request.user.is_authenticated:
        username = request.user.username

        # Read open matches from Redis DB
        open_matches = cache.get("openMatches") if cache.get("openMatches") is not None else []
        online_users = cache.get("onlineUsers") if cache.get("onlineUsers") is not None else []
        #print(open_matches)

        return render(request, "arena/arena.html", {"username": username, "game_levels": user_levels,
                                                    "open_matches": open_matches, "online_users": online_users})
    else:
        return render(request, "users/login.html",
                      {"message": "Please login first to start a new game!", "user": False,
                       "redirect_link": "arena", "game_levels": user_levels})


# game board initialization for match (player vs player)
def new_match(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        level = request.GET["difficulty"]
        mes = "Please login first to start a new game!"
        return render(request, "users/login.html", {"message": mes, "user": False, "level": level})

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
    game_db_entry = GameDB(user=user, score_p1=scores[0], score_p2=scores[1], player1=player1_name,
                           player2=player2_name,
                           next_player=1, game_over=False)
    game_db_entry.save()

    # save game state variables to session variables
    request.session["game_id"] = game_db_entry.id

    # save game to DB
    save_gamestate_db(new_game.board, game_db_entry.id, 0)

    json_response = {"game_id": game_db_entry.id}

    return JsonResponse(json_response, safe=False)



# initial game view
def reversi_match(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        redirect_link = "reversimatch"
        return HttpResponseRedirect(reverse("login"), {"redirect_link": redirect_link})

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
    # set session difficulty
    request.session["difficulty"] = difficulty

    print(f"Match: Green is {green_player} and Blue is {blue_player}.")

    user_color = "green" if user.username == green_player else "blue"

    return render(request, "reversimatch.html",
                  {"username": user.username,
                   "board": board,
                   "player1_name": green_player,
                   "player2_name": blue_player,
                   "game_level": difficulty,
                   "game_id": game_id,
                   "user_color": user_color,
                   "game_levels": user_levels
                   })


# Main Game Logic is executed in this view every time the current Player makes a move via browser input
# returns a json data object to browser which updates game board, scores and infos with JS
@require_http_methods(["POST"])
# @csrf_exempt
def move_match(request):
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

        # Something went wrong retrieving board (db error or cheating)
        if board is None:
            return render(request, "index.html", {"user": user, "game_levels": user_levels})

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
            # print("Illegal move!!!")
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
        # print(f'Not your turn {user.username}')
        scores = get_scores(board)
        message = f"Not your turn!"
        color = 'red'

    board_color = 'green' if next_player == 1 else 'blue'

    data = {"board": board, "message": {"message": message, "color": color},
            "next_player": next_player, "game_over": game_over,
            "scores": scores, "possible_moves": get_possible_moves(board, next_player), "board_color": board_color}

    return JsonResponse(data, safe=False)
