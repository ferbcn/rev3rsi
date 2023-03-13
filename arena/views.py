# arena/views.py
import os
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

game_levels = [('', 'easy'), ('', 'hard'), ('', 'harder'), ('disabled', 'hardest')]


@require_http_methods(["GET"])
def arenaindex(request):

    if request.user.is_authenticated:
        username = request.user.username

        nice_open_matches = []
        print("Open matches: ", nice_open_matches)

        return render(request, "arena/arena.html", {"open_matches": nice_open_matches, "username": username,
                                                   "game_levels": game_levels})
    else:
        return HttpResponseRedirect(reverse("login"))
