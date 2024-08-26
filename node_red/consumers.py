
import asyncio
import json
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
from .exmples import BaseWebSocketConsumer
class test(BaseWebSocketConsumer):
    url_external = "ws://localhost:1880/ws/mywebsocket/test"
    pass
