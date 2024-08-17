# simulator/views.py
import json

from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache

from reversi.game_levels import Levels

from reversi.game_logic import *
from reversi.data_layer import *


# Create an instance of the Levels class
levels_maker = Levels()
user_levels = levels_maker.get_levels()


@require_http_methods(["GET"])
def auto_game(request):
    if request.user is None or not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    else:
        user = request.user
        dummy_game = Game(difficulty="simulator", player1=None, player2=None)
        board = dummy_game.board
        board_color = "green"

        return render(request, "autogame.html", {"user": user, "board": board,
                                                 "game_levels": user_levels, "level": "auto-match",
                                                 "board_color": board_color})


@require_http_methods(["POST"])
def run_auto_game(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    try:
        data = json.loads(request.body)
        ai1_name = data["ai1_name"]
        ai2_name = data["ai2_name"]
        if random.choice([True, False]):
            player1, player2 = ai1_name, ai2_name
            p1_color = 'green'
            p2_color = 'blue'
        else:
            player1, player2 = ai2_name, ai1_name
            p1_color = 'blue'
            p2_color = 'green'
    except (KeyError, json.JSONDecodeError) as e:
        return JsonResponse({"error": str(e)}, status=400)

    # New Game and board initialization
    difficulty = "auto-match"
    new_game = Game(player1, player2, difficulty, board=None)
    scores = get_scores(new_game.board)
    print("NEW GAME STARTED! Difficulty: ", difficulty)

    # save game to DB
    game_db_entry = GameDB(user=user, score_p1=scores[0], score_p2=scores[1], player1=player1,
                           player2=player2, next_player=1, game_over=False)
    game_db_entry.save()
    game_id = game_db_entry.id
    print("GAME Entry: ", game_id)

    # Save Session variable
    prev_state_id = 0

    # save gamestate to DB
    save_gamestate_db(new_game.board, game_id, prev_state_id)

    # Load gamestate from db
    board, player1_name, player2_name, next_player, state_id = load_gamestate_db(game_id, user)

    game_over = False
    player1_maker = AiMachinePlayerMaker(player1_name, 1)
    player1 = player1_maker.get_player()

    player2_maker = AiMachinePlayerMaker(player2_name, 2)
    player2 = player2_maker.get_player()

    while not game_over:
        # Player moves
        next_player_name = player1_name if next_player == 1 else player2_name
        print(f"### Player{next_player} {next_player_name} possible moves:")
        possible_moves = get_possible_moves(board, next_player)
        print(possible_moves)

        next_player_instance = player1 if next_player == 1 else player2
        # Make a move
        next_move, board = machine_move(board, next_player_instance)
        message = f"Player{next_player} made move: row {next_move[0] + 1}, col {next_move[1] + 1}"
        print(message)
        next_player = get_opponent(next_player)

        # save gamestate to DB
        save_gamestate_db(board, game_id, state_id)

        # Check for Game Over
        if len(get_possible_moves(board, next_player)) == 0:
            next_player = get_opponent(next_player)
            if len(get_possible_moves(board, next_player)) == 0:
                game_over = True

    scores = get_scores(board)
    if scores[0] == scores[1]:
        winner = "draw"
        winner_role = 0
        board_color = 'lightgrey'
        message = "It's a draw!"
    else:
        winner = player1_name if scores[0] > scores[1] else player2_name
        if ai1_name == player1_name:
            winner_role = 1 if scores[0] > scores[1] else 2
        else:
            winner_role = 2 if scores[0] > scores[1] else 1
        message = f"Machine{winner_role} ({winner}) has won!"
        board_color = 'green' if winner_role == 1 else 'blue'

    print(f"### Game ended, {message}!")
    print(f"Final Score: {scores[0]} - {scores[1]}")

    # Save final scores and winner to DB
    save_game_db(game_id, scores[0], scores[1], winner_role, game_over)

    # Calculate elo rating
    elo_player1 = get_rating_for_user(player1_name)
    if elo_player1 is None:
        create_base_rating_for_user(player1_name)
        elo_player1 = get_rating_for_user(player1_name)
    elo_player2 = get_rating_for_user(player2_name)
    if elo_player2 is None:
        create_base_rating_for_user(player2_name)
        elo_player2 = get_rating_for_user(player1_name)
    print(f"Current ELO-ratings: Player1 ({player1_name}): {elo_player1}, Player2 ({player2_name}): {elo_player2}")

    new_elo_p1 = int(elo_player1 + (scores[0] - scores[1]) * (elo_player1/elo_player2))
    new_elo_p2 = int(elo_player2 + (scores[1] - scores[0]) * (elo_player2/elo_player1))
    print(f"New ELO-ratings: Player1 ({player1_name}): {new_elo_p1}, Player2 ({player2_name}): {new_elo_p2}")

    # Update ratings in DB
    if winner_role == 0:
        update_ratings_for_user_game(player1_name, new_elo_p1, 0)
        update_ratings_for_user_game(player2_name, new_elo_p2, 0)
    else:
        update_ratings_for_user_game(player1_name, new_elo_p1, 1 if winner_role == 1 else -1)
        update_ratings_for_user_game(player2_name, new_elo_p2, 1 if winner_role == 2 else -1)


    data = {"board": board, "message": {"message": message}, winner: winner, "scores": scores,
            "player1_name": player1_name, "player2_name": player2_name, "p1_color": p1_color, "p2_color": p2_color,
            "board_color": board_color}

    return JsonResponse(data)
