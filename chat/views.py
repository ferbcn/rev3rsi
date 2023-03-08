# chat/views.py
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

import redis

game_levels = [('', 'easy'), ('', 'hard'), ('', 'harder'), ('disabled', 'hardest')]


@require_http_methods(["GET"])
def arenaindex(request):
    conn = redis.Redis('localhost')
    if request.user.is_authenticated:
        username = request.user.username

        # Read open matches from Redis DB
        open_matches = conn.hgetall("openMatches")
        nice_open_matches = []
        for match, host in open_matches.items():
            match_name = match.decode("utf-8")
            match_host = host.decode("utf-8")
            nice_open_matches.append((match_name, match_host))
        print("Open matches: ", nice_open_matches)

        return render(request, "chat/arena.html", {"open_matches": nice_open_matches, "username": username,
                                                   "game_levels": game_levels})
    else:
        return HttpResponseRedirect(reverse("login"))
