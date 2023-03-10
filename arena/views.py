# arena/views.py
import os
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods


#import redis
#REDIS_HOST = os.environ.get("REDIS_HOST")
#conn = redis.Redis(host=REDIS_HOST)

game_levels = [('', 'easy'), ('', 'hard'), ('', 'harder'), ('disabled', 'hardest')]


@require_http_methods(["GET"])
def arenaindex(request):

    if request.user.is_authenticated:
        username = request.user.username

        # Read open matches from Redis DB
        nice_open_matches = []
        """
        for match, host in open_matches.items():
            match_name = match.decode("utf-8")
            match_host = host.decode("utf-8")
            nice_open_matches.append((match_name, match_host))
        """
        print("Open matches: ", nice_open_matches)

        return render(request, "arena/arena.html", {"open_matches": nice_open_matches, "username": username,
                                                   "game_levels": game_levels})
    else:
        return HttpResponseRedirect(reverse("login"))
