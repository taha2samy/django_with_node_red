from django.urls import path
from .consumers.nodered import NodeRed

websocket_urlpatterns = [
    path('ws/device', NodeRed.as_asgi()),  # Define your WebSocket URL pattern
]


