# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.arenaindex, name="arenaindex"),
]