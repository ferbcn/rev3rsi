# simulator/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("autogame", views.auto_game, name="autogame"),
    path("runautogame", views.run_auto_game, name="run_auto_game"),
]