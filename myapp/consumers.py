
import asyncio
import json
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
from .exmples import BaseWebSocketConsumer
class test(BaseWebSocketConsumer):
    url_external = "ws://localhost:1880/ws/mywebsocket/test"
    pass
class ForbiddenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Reject the connection with a forbidden status
        await self.close(code=403)  # 403 is not a standard WebSocket close code, but this indicates forbidden
