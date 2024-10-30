from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("reversi", views.reversi, name="reversi"),
    path("register", views.register, name="register"),
    path("newgame", views.new_game, name="newgame"),
    path("move", views.move, name="move"),
    path("queryboard/", views.query_board, name="queryboard"),
    path("savedgames", views.saved_games, name="savedgames"),
    path("savedgamespage", views.saved_games_page, name="savedgamespage"),
    path("savedratings", views.saved_ratings, name="savedratings"),
    path("loadgame", views.load_game, name="loadgame"),
    path("deletegame", views.delete_game, name="deletegame"),
    # path("newmatch", views.new_match, name="newmatch"),
    # path("reversimatch", views.reversi_match, name="reversimatch"),
    # path("movematch", views.move_match, name="movematch"),
    # path("load_prev_gamestate", views.load_prev_gamestate, name="load_prev_gamestate"),
]