# arena/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.arenaindex, name="arenaindex"),
    #path("arena/", views.arenaindex, name="arenaindex"),
]