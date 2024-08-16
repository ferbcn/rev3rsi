# arena/views.py
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache

from reversi.game_levels import Levels

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
        return HttpResponseRedirect(reverse("login"))
