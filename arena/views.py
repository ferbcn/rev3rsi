# arena/views.py
import os
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache

# import redis
# REDIS_HOST = os.environ.get("REDIS_HOST")
# conn = redis.Redis(host=REDIS_HOST)

game_levels = [('', 'easy'), ('', 'hard'), ('', 'harder'), ('disabled', 'hardest')]


@require_http_methods(["GET"])
def arenaindex(request):
    if request.user.is_authenticated:
        username = request.user.username

        # Read open matches from Redis DB
        #cache.set('openMatches', [('1c0abd9f-31a3-4da7-9040-ea61c1edc367', 'fer')], 30)
        open_matches = cache.get("openMatches")
        #print(open_matches)

        return render(request, "arena/arena.html", {"open_matches": open_matches, "username": username,
                                                    "game_levels": game_levels})
    else:
        return HttpResponseRedirect(reverse("login"))
