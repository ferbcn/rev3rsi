# arena/views.py
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache

game_levels = [('', 'easy'), ('', 'hard'), ('', 'harder'), ('disabled', 'hardest')]


@require_http_methods(["GET"])
def arenaindex(request):
    if request.user.is_authenticated:
        username = request.user.username

        # Read open matches from Redis DB
        open_matches = cache.get("openMatches")
        online_users = cache.get("onlineUsers")
        #print(open_matches)

        return render(request, "arena/arena.html", {"username": username, "game_levels": game_levels,
                                                    "open_matches": open_matches, "online_users": online_users})
    else:
        return HttpResponseRedirect(reverse("login"))
