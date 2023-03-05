# chat/views.py
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

game_levels = [('', 'easy'), ('', 'hard'), ('', 'harder'), ('disabled', 'hardest')]

import redis
conn = redis.Redis('localhost')

def chatindex(request):
    if request.user.is_authenticated:
        username = request.user.username

        # Read open matches from Redis DB
        open_matches = conn.hgetall("openMatches")
        nice_open_matches = []
        for match in open_matches:
            name = match.decode("utf-8")
            host = open_matches.get(match).decode("utf-8")
            nice_open_matches.append((name, host))
        print("Open matches: ", nice_open_matches)
        return render(request, "chat/arena.html", {"open_matches": nice_open_matches, "username": username, "game_levels": game_levels})
    else:
        return HttpResponseRedirect(reverse("login"))


def room(request, room_name):
    if request.user.is_authenticated:
        username = request.user.username
        return render(request, "chat/room.html", {"room_name": room_name, "username": username})
    else:
        return HttpResponseRedirect(reverse("login"))
