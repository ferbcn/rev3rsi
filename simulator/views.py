# simulator/views.py
import asyncio
import json
from asgiref.sync import sync_to_async
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from reversi.game_levels import Levels
from reversi.game_logic import *
from reversi.data_layer import *
from .queue_processor import game_queue

# Create an instance of the Levels class
levels_maker = Levels()
user_levels = levels_maker.get_levels()


@require_http_methods(["GET"])
def auto_game(request):
    if request.user is None or not request.user.is_authenticated:
        return render(request, "users/login.html",
                      {"message": "Please login first to start a new game!", "user": False,
                       "redirect_link": "simulator", "game_levels": user_levels})
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
    except (KeyError, json.JSONDecodeError) as e:
        return JsonResponse({"error": str(e)}, status=400)

    game_data = {
        'user': user,
        'ai1_name': ai1_name,
        'ai2_name': ai2_name
    }
    game_queue.put(game_data)

    return JsonResponse({"message": "Game is being processed, pos in queue: " + str(game_queue.qsize())})


@sync_to_async
def get_last_saved_game_id_async():
    return get_last_saved_game_id()


@sync_to_async
def load_game_object_data_async(game_id):
    return load_game_object_data(game_id)


@sync_to_async
def load_gamestate_db_async(game_id):
    return load_gamestate_board(game_id)

@sync_to_async
def get_ratings_for_user_async(user):
    return get_ratings_for_user(user)


async def sse_stream(request):
    """
    Sends server-sent events to the client.
    """
    async def event_stream():
        # yield finished game data
        last_game_id = await get_last_saved_game_id_async()
        while True:
            # check for new game_id
            new_game_id = await get_last_saved_game_id_async()
            if not new_game_id == last_game_id:
                data = await load_game_object_data_async(new_game_id)
                ratings1 = await get_ratings_for_user_async(data.player1)
                ratings2 = await get_ratings_for_user_async(data.player2)
                board_data = await load_gamestate_db_async(new_game_id)
                winner_role = 0 if data.score_p1 == data.score_p2 else (1 if data.score_p1 > data.score_p2 else 2)
                board_color = 'lightgrey' if winner_role == 0 else ('green' if winner_role == 1 else 'blue')
                json_response = json.dumps({"player1": data.player1, "player2": data.player2,
                                            "score_p1": data.score_p1, "score_p2": data.score_p2,
                                            "board": board_data, "game_over": data.game_over,
                                            "board_color": board_color,
                                            "queue_size": game_queue.qsize(),
                                            "elo_p1": ratings1.elo, "elo_p2": ratings2.elo,})
                if data.game_over:
                    last_game_id = new_game_id
                    await asyncio.sleep(1)
                    yield f'data: {json_response} \n\n'
            await asyncio.sleep(1)

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


@require_http_methods(["GET"])
def saved_elo_ratings(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        return HttpResponseRedirect(reverse("login"))

    saved_ratings = get_ratings_for_all_users()

    return render(request, "eloratings.html",
                  {"user": user, "saved_ratings": saved_ratings, "game_levels": user_levels})
