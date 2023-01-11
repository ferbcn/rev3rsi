from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("reversi", views.reversi, name="reversi"),
    path("register", views.register, name="register"),
    path("newgame", views.newgame, name="newgame"),
    path("move", views.move, name="move"),
    path("savedgames", views.savedgames, name="savedgames"),
    path("loadgame", views.loadgame, name="loadgame"),
    path("deletegame", views.deletegame, name="deletegame"),
]
