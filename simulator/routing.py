# arena/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/simulator/", consumers.ArenaConsumer.as_asgi()),
]