from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import websockets
import json
from django.core.cache import cache
from datetime import datetime


class BaseWebSocketConsumer(AsyncWebsocketConsumer):
    url_external = "ws://example.com"  # Change to the actual URL
    group_name = "group_name"  # Override in subclass
    status_key = "status_key"  # Override in subclass
    cache_time = None

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Connect to external WebSocket
        await self.connect_external_ws()

        # Start receiving messages from external WebSocket
        self.external_ws_task = asyncio.create_task(self.receive_from_external_ws())

        # Send initial status if available
        last_message = cache.get(self.status_key, None)
        if last_message:
            await self.send(text_data=json.dumps({'message': last_message}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'external_ws_task'):
            self.external_ws_task.cancel()
        if hasattr(self, 'websocket') and self.websocket:
            await self.websocket.close()

    async def receive(self, text_data):
        message = json.loads(text_data)
        await self.send_to_external_ws(message)

    async def receive_from_external_ws(self):
        while True:
            try:
                message = json.loads(await self.websocket.recv())
                message["is_disconnected"] = False
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
                last_message = cache.get(self.status_key, {})
                if reconnection_attempts == 1:
                    last_message["disconnected_at"] = datetime.now().isoformat()
                last_message["reconnection_attempts"] = reconnection_attempts
                last_message["is_disconnected"] = True
                cache.set(self.status_key, last_message, self.cache_time)
                await self.send(text_data=json.dumps({'message': last_message}))

                await asyncio.sleep(5)
                await self.connect_external_ws()
                break
            except Exception:
                pass

        # Clear disconnection status after successful reconnection
        last_message = cache.get(self.status_key, {})
        last_message.pop("disconnected_at", None)
        last_message.pop("reconnection_attempts", None)
        last_message["is_disconnected"] = False
        cache.set(self.status_key, last_message, self.cache_time)
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'send_message', 'message': last_message}
        )

    async def connect_external_ws(self):
        try:
            self.websocket = await websockets.connect(self.url_external)
        except Exception as e:
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
        last_stored_message = cache.get(self.status_key, None)
        if message != last_stored_message:
            cache.set(self.status_key, message, self.cache_time)
            await self.channel_layer.group_send(
                self.group_name,
                {'type': 'send_message', 'message': message}
            )


class BaseSlider(BaseWebSocketConsumer):
    group_name = "switch_button_group"
    status_key = "switch_button_status"


class BaseSwitchButton(BaseWebSocketConsumer):
    group_name = "switch_button_group"
    status_key = "switch_button_status"


class BaseButton(BaseWebSocketConsumer):
    group_name = "button_group"
    status_key = "button_status"


class BaseSeries(BaseWebSocketConsumer):
    url_external = "ws://example.com"  # Change to the actual URL
    group_name = "button_group"
    status_key = "button_status"
    max_points = 10
    cache_time = None

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.connect_external_ws()
        self.points = cache.get(self.status_key, [])
        for point in self.points:
            await self.send(text_data=json.dumps({'message': point}))
        self.external_ws_task = asyncio.create_task(self.receive_from_external_ws())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'external_ws_task'):
            self.external_ws_task.cancel()
        if hasattr(self, 'websocket') and self.websocket:
            await self.websocket.close()

    async def receive_from_external_ws(self):
        reconnection_attempts = 0
        while True:
            try:
                message = json.loads(await self.websocket.recv())
                point = {'x': message.get('x'), 'y': message.get('y')}
                self.points.append(point)
                if len(self.points) > self.max_points:
                    self.points.pop(0)
                cache.set(self.status_key, self.points, self.cache_time)
                await self.channel_layer.group_send(
                    self.group_name,
                    {'type': 'send_message', 'message': message}
                )
                reconnection_attempts = 0  # Reset reconnection attempts on successful reception
            except websockets.ConnectionClosed:
                await self.handle_disconnection()

    async def handle_disconnection(self):
        reconnection_attempts = 0
        connected = False
        while not connected:
            try:
                reconnection_attempts += 1
                last_message = {
                    "x": None,
                    "y": None,
                    "is_disconnected": True,
                    "reconnection_attempts": reconnection_attempts,
                    "disconnected_at": datetime.now().isoformat()
                }
                cache.set(self.status_key, last_message, self.cache_time)
                await self.send(text_data=json.dumps({'message': last_message}))
                await asyncio.sleep(5)  # Adjust the delay as needed
                await self.connect_external_ws()
                connected = True
            except Exception as e:
                # Log or handle the exception as needed
                pass

        last_message = cache.get(self.status_key, {})
        if isinstance(last_message, dict):
            last_message.pop("disconnected_at", None)
            last_message.pop("reconnection_attempts", None)
            last_message["is_disconnected"] = False
            cache.set(self.status_key, last_message, self.cache_time)
            await self.channel_layer.group_send(
                self.group_name,
                {'type': 'send_message', 'message': last_message}
            )


