# arena/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/simulator/auto", consumers.SimulatorConsumer.as_asgi()),
]