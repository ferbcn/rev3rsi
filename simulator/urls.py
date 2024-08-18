# simulator/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.auto_game, name="autogame"),
    path("autogame", views.auto_game, name="autogame"),
    path("runautogame", views.run_auto_game, name="run_auto_game"),
    path('streamindex', views.stream_index, name='index'),
    path('stream/', views.sse_stream, name='sse_stream'),
]