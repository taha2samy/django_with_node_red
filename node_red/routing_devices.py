from django.urls import path
from .consumers.nodered import NodeRed

websocket_urlpatterns = [
    path('device/node_red/nodered1', NodeRed.as_asgi()),  # Define your WebSocket URL pattern
]


