from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import websockets
import json
from django.core.cache import cache
from datetime import datetime
from .models import Devices
from asgiref.sync import sync_to_async
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import websockets
from datetime import datetime

class BaseWebSocketConsumer(AsyncWebsocketConsumer):
    url_external = "ws://example.com"  # Change to the actual URL
    max_messages = 5  # Maximum number of messages to store
    last_messages = []  # Store last messages in memory

    async def get_check_device(self, group_id):
        device = await sync_to_async(Devices.objects.get)(Device_id=group_id)
        data = {attr.name: getattr(device, attr.name) for attr in device._meta.fields}
        return data

    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs'].get('group_id')
        data = await self.get_check_device(self.group_name)
        
        if not data:
            await self.close(code=403)

        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        self.max_messages = data['points']
        self.user = str(self.scope["user"])

        await self.connect_external_ws()

        self.external_ws_task = asyncio.create_task(self.receive_from_external_ws())
        print(self.group_name)
        last_messages = cache.get(self.group_name, [])
        print("length",self.group_name,len(last_messages))
        for message in last_messages:
            await self.send(text_data=json.dumps({'message': message}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'external_ws_task'):
            self.external_ws_task.cancel()
        if hasattr(self, 'websocket') and self.websocket:
            await self.websocket.close()

    async def receive(self, text_data):
        message = json.loads(text_data)
        message["group_id"] = self.group_name
        message["user"] = self.user
        await self.send_to_external_ws(message)

    async def receive_from_external_ws(self):
        while True:
            try:
                message = json.loads(await self.websocket.recv())
                message["is_disconnected"] = False
                if message["group_id"] == self.group_name:
                    await self.handle_message(message)
            except websockets.ConnectionClosed:
                await self.handle_disconnection()
            except Exception:
                break

    async def handle_disconnection(self):
        reconnection_attempts = 0
        while True:
            try:
                reconnection_attempts += 1
                last_message = {
                    "is_disconnected": True,
                    "reconnection_attempts": reconnection_attempts,
                    "disconnected_at": datetime.now().isoformat() if reconnection_attempts == 1 else None
                }

                await self.send(text_data=json.dumps({'message': last_message}))

                await asyncio.sleep(5)
                await self.connect_external_ws()
                break
            except Exception:
                pass

        # Update last message on reconnection
        last_message = {"is_disconnected": False}
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'send_message', 'message': last_message}
        )

    async def connect_external_ws(self):
        try:
            self.websocket = await websockets.connect(self.url_external)
        except Exception:
            await self.handle_disconnection()

    async def send_to_external_ws(self, message):
        try:
            if self.websocket and self.websocket.open:
                await self.websocket.send(json.dumps(message))
        except websockets.ConnectionClosed:
            await self.handle_disconnection()
        except Exception:
            pass

    async def send_message(self, event):
        await self.send(text_data=json.dumps({'message': event['message']}))

    async def handle_message(self, message):

            await self.channel_layer.group_send(
                self.group_name,
                {'type': 'send_message', 'message': message}
            )
