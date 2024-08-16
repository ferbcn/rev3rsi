# arena/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.arena_index, name="arenaindex"),
    #path("arena/", views.arenaindex, name="arenaindex"),
]