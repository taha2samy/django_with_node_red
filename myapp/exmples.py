from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import websockets
import json
from django.core.cache import cache
from datetime import datetime


class BaseSlider(AsyncWebsocketConsumer):
    url_external = "ws://example.com"  # Change to the actual URL
    group_name = "switch_button_group"
    status_key = "switch_button_status"  # Cache key for storing status
    cache_time = None

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        try:
            self.websocket = await websockets.connect(self.url_external)
        except Exception as e:
            await self.handle_disconnection()
        
        self.external_ws_task = asyncio.create_task(self.receive_from_external_ws())

        # Reconnection successful, check if the last cached message contains disconnection details
        last_message = cache.get(self.status_key, None)
        if last_message:
            await self.send(text_data=json.dumps({'message': last_message}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'external_ws_task'):
            self.external_ws_task.cancel()
        if hasattr(self, 'websocket'):
            await self.websocket.close()

    async def receive(self, text_data):
        message = json.loads(text_data)
        await self.send_to_external_ws(message)

    async def receive_from_external_ws(self):
        while True:
            try:
                message = json.loads(await self.websocket.recv())
                message["is_disconnected"] = False
                last_stored_message = cache.get(self.status_key, None)

                if message != last_stored_message:
                    cache.set(self.status_key, message, self.cache_time)
                    await self.channel_layer.group_send(
                        self.group_name,
                        {'type': 'send_message', 'message': message}
                    )

            except websockets.ConnectionClosed:
                await self.handle_disconnection()

            except Exception as e:
                break

    async def handle_disconnection(self):
        reconnection_attempts = 0
        connected = False

        while not connected:
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

                try:
                    self.websocket = await websockets.connect(self.url_external)
                    connected = True
                except Exception as e:
                    pass

            except Exception as e:
                pass

        # When reconnection is successful, clean up the cached message
        last_message.pop("disconnected_at", None)
        last_message.pop("reconnection_attempts", None)
        last_message["is_disconnected"] = False

        cache.set(self.status_key, last_message, self.cache_time)
        if self.channel_layer:
            await self.channel_layer.group_send(
                self.group_name,
                {'type': 'send_message', 'message': last_message}
            )

    async def send_to_external_ws(self, message):
        try:
            if self.websocket and self.websocket.open:
                await self.websocket.send(json.dumps(message))
        except websockets.ConnectionClosed:
            await self.handle_disconnection()
        except Exception as e:
            pass

    async def send_message(self, event):
        await self.send(text_data=json.dumps({'message': event['message']}))

class BaseSwitchButton(AsyncWebsocketConsumer):
    url_external = "ws://example.com"  # Change to the actual URL
    group_name = "switch_button_group"
    status_key = "switch_button_status"  # Cache key for storing status
    cache_time = None

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        try:
            self.websocket = await websockets.connect(self.url_external)
            pass
        except Exception as e:
            pass
            await self.handle_disconnection()

        # Retrieve the status from cache
        self.status = cache.get(self.status_key, None)  # Default to None if not set

        # Start receiving messages from the external WebSocket
        self.external_ws_task = asyncio.create_task(self.receive_from_external_ws())

        # Send the initial status after connecting to the external WebSocket
        if self.status is not None:
            await self.send(text_data=json.dumps({'message': self.status}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'external_ws_task'):
            self.external_ws_task.cancel()
        if hasattr(self, 'websocket') and self.websocket:
            await self.websocket.close()
        pass

    async def receive(self, text_data):
        try:
            message = json.loads(text_data)
            await self.send_to_external_ws(message)
        except json.JSONDecodeError as e:
            pass
    async def receive_from_external_ws(self):
        while True:
            try:
                message = await self.websocket.recv()
                message = json.loads(message)
                last_stored_message = cache.get(self.status_key, None)
                if message != last_stored_message:
                    self.status = message.get('payload', self.status)
                    # Store the status in cache
                    cache.set(self.status_key, message, self.cache_time)

                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'send_message',
                            'message': message,
                        }
                    )
            except websockets.ConnectionClosed:
                await self.handle_disconnection()
            except Exception as e:
                break

    async def handle_disconnection(self):
        reconnection_attempts = 0
        connected = False

        while not connected:
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

                try:
                    self.websocket = await websockets.connect(self.url_external)
                    connected = True
                except Exception as reconnect_exception:
                    pass

            except Exception as e:
                pass
        # When reconnection is successful, clean up the cached message
        last_message = cache.get(self.status_key, {})
        last_message.pop("disconnected_at", None)
        last_message.pop("reconnection_attempts", None)
        last_message["is_disconnected"] = False

        cache.set(self.status_key, last_message, self.cache_time)
        if self.channel_layer:
            await self.channel_layer.group_send(
                self.group_name,
                {'type': 'send_message', 'message': last_message}
            )

    async def send_to_external_ws(self, message):
        try:
            if self.websocket and self.websocket.open:
                await self.websocket.send(json.dumps(message))
        except websockets.ConnectionClosed:
            
            await self.handle_disconnection()
        except Exception as e:
            pass

    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))


class BaseButton(AsyncWebsocketConsumer):
    url_external = "ws://example.com"  
    group_name = "button_group"
    status_key = "button_status" 
    cache_time = None

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        try:
            self.websocket = await websockets.connect(self.url_external)
            
        except Exception as e:
            
            await self.handle_disconnection()

        # Retrieve the status from cache
        self.status = cache.get(self.status_key, None)  # Default to None if not set

        # Start receiving messages from the external WebSocket
        self.external_ws_task = asyncio.create_task(self.receive_from_external_ws())

        # Send the initial status after connecting to the external WebSocket
        if self.status is not None:
            await self.send(text_data=json.dumps({'message': self.status}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'external_ws_task'):
            self.external_ws_task.cancel()
        if hasattr(self, 'websocket') and self.websocket:
            await self.websocket.close()

    async def receive(self, text_data):
        try:
            message = json.loads(text_data)
            await self.send_to_external_ws(message)
        except json.JSONDecodeError as e:
            pass

    async def receive_from_external_ws(self):
        reconnection_attempts = 0
        while True:
            try:
                message = await self.websocket.recv()
                message = json.loads(message)
                message["is_disconnected"] = False
                last_stored_message = cache.get(self.status_key, None)

                if message != last_stored_message:
                    self.status = message.get('payload', self.status)
                    cache.set(self.status_key, message, self.cache_time)

                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'send_message',
                            'message': message,
                        }
                    )
                    reconnection_attempts = 0  # Reset reconnection attempts on successful reception

            except websockets.ConnectionClosed:
                await self.handle_disconnection()
            except Exception as e:
                break

    async def handle_disconnection(self):
        reconnection_attempts = 0
        connected = False

        while not connected:
            try:
                reconnection_attempts += 1
                last_message = cache.get(self.status_key, {})
                
                if reconnection_attempts == 1:
                    last_message["disconnected_at"] = datetime.now().isoformat()
                
                last_message["reconnection_attempts"] = reconnection_attempts
                last_message["is_disconnected"] = True

                cache.set(self.status_key, last_message, self.cache_time)
                await self.send(text_data=json.dumps({'message': last_message}))

                

                await asyncio.sleep(5)  # Adjust the delay as needed

                try:
                    self.websocket = await websockets.connect(self.url_external)
                    connected = True
                    
                except Exception as e:
                    pass

            except Exception as e:
                pass

        # When reconnection is successful, clean up the cached message
        last_message = cache.get(self.status_key, {})
        last_message.pop("disconnected_at", None)
        last_message.pop("reconnection_attempts", None)
        last_message["is_disconnected"] = False

        cache.set(self.status_key, last_message, self.cache_time)
        if self.channel_layer:
            await self.channel_layer.group_send(
                self.group_name,
                {'type': 'send_message', 'message': last_message}
            )

    async def send_to_external_ws(self, message):
        try:
            if self.websocket and self.websocket.open:
                await self.websocket.send(json.dumps(message))
        except websockets.ConnectionClosed:
            await self.handle_disconnection()
        except Exception as e:
            pass
    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))



class BaseSeries(AsyncWebsocketConsumer):
    url_external = "ws://example.com"
    group_name = "button_group"
    status_key = "button_status"
    max_points = 10  
    cache_time=None
    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        try:
            self.websocket = await websockets.connect(self.url_external)
        except Exception as e:
            await self.handle_disconnection()

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
                # Try to receive a message from the external WebSocket
                message = await self.websocket.recv()
                message = json.loads(message)
                point = {'x': message['x'], 'y': message['y']}

                self.points.append(point)
                if len(self.points) > self.max_points:
                    self.points.pop(0)
                
                # Store the points in the cache
                cache.set(self.status_key, self.points, self.cache_time)

                # Remove connection status entries from cache on successful reception

                # Prepare the message with connection details


                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'send_message',
                        'message': message,
                    }
                )
                
                reconnection_attempts = 0  # Reset reconnection attempts on successful reception

            except websockets.ConnectionClosed:
                await self.handle_disconnection()

    async def handle_disconnection(self):
        reconnection_attempts = 0
        connected = False
        date = datetime.now().isoformat()
        while not connected:

            try:
                reconnection_attempts += 1
                last_message = {"x": None,"y":None, "is_disconnected": True, "reconnection_attempts": 0}

                # Ensure last_message is a dictionary
                
                last_message["disconnected_at"] = date
                last_message["reconnection_attempts"] = reconnection_attempts
                last_message["is_disconnected"] = True

                cache.set(self.status_key, last_message, self.cache_time)
                await self.send(text_data=json.dumps({'message': last_message}))


                await asyncio.sleep(5)  # Adjust the delay as needed

                try:
                    self.websocket = await websockets.connect(self.url_external)
                    connected = True
                except Exception as e:
                    pass
            except:
                pass
        # When reconnection is successful, clean up the cached message
        last_message = cache.get(self.status_key, {})
        if isinstance(last_message, dict):
            last_message.pop("disconnected_at", None)
            last_message.pop("reconnection_attempts", None)
            last_message["is_disconnected"] = False

            cache.set(self.status_key, last_message, self.cache_time)
            if self.channel_layer:
                await self.channel_layer.group_send(
                    self.group_name,
                    {'type': 'send_message', 'message': last_message}
                )

                # Wait before trying to reconnect
                await asyncio.sleep(5)  # Adjust the delay as needed

    async def send_message(self, event):
        point = event['message']
        await self.send(text_data=json.dumps({'message': point}))
