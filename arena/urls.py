# arena/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.arena_index, name="arenaindex"),
    #path("arena/", views.arenaindex, name="arenaindex"),
    path("newmatch", views.new_match, name="newmatch"),
    path("reversimatch", views.reversi_match, name="reversimatch"),
    path("movematch", views.move_match, name="movematch"),
]