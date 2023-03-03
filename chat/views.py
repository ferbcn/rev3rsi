# chat/views.py
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

game_levels = [('', 'easy'), ('', 'hard'), ('', 'harder'), ('disabled', 'hardest')]

def chatindex(request):
    if request.user.is_authenticated:
        username = request.user.username
        # dummy list -> get from Redis Chache???
        room_list = ["TheLobby", "war8oom", "chill0ut"]
        return render(request, "chat/arena.html", {"room_list": room_list, "username": username, "game_levels": game_levels})
    else:
        return HttpResponseRedirect(reverse("login"))


def room(request, room_name):
    if request.user.is_authenticated:
        username = request.user.username
        return render(request, "chat/room.html", {"room_name": room_name, "username": username})
    else:
        return HttpResponseRedirect(reverse("login"))
