from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import websockets
import json
from django.core.cache import cache

class BaseSwitchButton(AsyncWebsocketConsumer):
    url_external = "ws://example.com"  # Change to the actual URL
    group_name = "switch_button_group"
    status_key = "switch_button_status"  # Cache key for storing status

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        try:
            self.websocket = await websockets.connect(self.url_external)
        except Exception as e:
            raise Exception(f"Cannot connect to {self.url_external}: {e}")

        # Retrieve the status from cache
        self.status = cache.get(self.status_key, None)  # Default to None if not set

        # Send the initial status after connecting to the external WebSocket
        self.external_ws_task = asyncio.create_task(self.receive_from_external_ws())

        if self.status is not None:
            await self.send(text_data=json.dumps({'message': self.status}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'external_ws_task'):
            self.external_ws_task.cancel()
        if self.websocket:
            await self.websocket.close()

    async def receive(self, text_data):
        message = json.loads(text_data)
        if message.get('payload') == 'on':
            self.status = True
            message["payload"] = self.status
        elif message.get('payload') == 'off':
            self.status = False
            message["payload"] = self.status

        await self.send_to_external_ws(message)

    async def receive_from_external_ws(self):
        while True:
            try:
                message = await self.websocket.recv()
                message = json.loads(message)
                last_stored_message = cache.get(self.status_key, None)
                if message != last_stored_message:
                    self.status = message.get('payload', self.status)
                    # Store the status in cache
                    cache.set(self.status_key, message)

                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'send_message',
                            'message': message,
                        }
                    )
            except websockets.ConnectionClosed:
                print("Connection to the external WebSocket closed")
                break
            except Exception as e:
                print(f"An error occurred while receiving: {e}")
                break

    async def send_to_external_ws(self, message):
        try:
            if self.websocket and self.websocket.open:
                await self.websocket.send(json.dumps(message))
        except websockets.ConnectionClosed:
            print("Connection to the external WebSocket closed while sending")
        except Exception as e:
            print(f"An error occurred while sending: {e}")

    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))

class BaseButton(AsyncWebsocketConsumer):
    url_external = "ws://example.com"  
    group_name = "button_group"
    status_key = "button_status" 

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        try:
            self.websocket = await websockets.connect(self.url_external)
        except Exception as e:
            raise Exception(f"Cannot connect to {self.url_external}: {e}")

        # Retrieve the status from cache
        self.status = cache.get(self.status_key, None)  # Default to None if not set

        # Send the initial status after connecting to the external WebSocket
        self.external_ws_task = asyncio.create_task(self.receive_from_external_ws())

        if self.status is not None:
            await self.send(text_data=json.dumps({'message': self.status}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'external_ws_task'):
            self.external_ws_task.cancel()
        if self.websocket:
            await self.websocket.close()

    async def receive(self, text_data):
        message = json.loads(text_data)
       
        await self.send_to_external_ws(message)

    async def receive_from_external_ws(self):
        while True:
            try:
                message = await self.websocket.recv()
                message = json.loads(message)
                print("11111",message)
                # Store the last received message in cache
                cache.set(self.status_key, message)

                # Send message to the specified group
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'send_message',
                        'message': message,
                    }
                )
            except websockets.ConnectionClosed:
                print("Connection to the external WebSocket closed")
                break
            except Exception as e:
                print(f"An error occurred while receiving: {e}")
                break

    async def send_to_external_ws(self, message):
        try:
            if self.websocket and self.websocket.open:
                await self.websocket.send(json.dumps(message))
        except websockets.ConnectionClosed:
            print("Connection to the external WebSocket closed while sending")
        except Exception as e:
            print(f"An error occurred while sending: {e}")

    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))



class Series(AsyncWebsocketConsumer):
    url_external = "ws://example.com"
    group_name = "button_group"
    status_key = "button_status"
    max_points = 10  # الحد الأقصى للنقاط المخزنة

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        try:
            self.websocket = await websockets.connect(self.url_external)
        except Exception as e:
            raise Exception(f"Cannot connect to {self.url_external}: {e}")

        # استرجاع النقاط المخزنة من الكاش
        self.points = cache.get(self.status_key, [])  # افتراض قائمة فارغة إذا لم تكن موجودة

        # إرسال النقاط المخزنة للعميل
        for point in self.points:
            await self.send(text_data=json.dumps({'message': point}))

        # إنشاء مهمة لاستقبال الرسائل من WebSocket خارجي
        self.external_ws_task = asyncio.create_task(self.receive_from_external_ws())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'external_ws_task'):
            self.external_ws_task.cancel()
        if hasattr(self, 'websocket') and self.websocket:
            await self.websocket.close()

    async def receive_from_external_ws(self):
        while True:
            try:
                message = await self.websocket.recv()
                message = json.loads(message)
                # افترض أن الرسالة تحتوي على النقاط في الشكل {'x': value, 'y': value}
                point = {'x': message['x'], 'y': message['y']}

                # إضافة النقطة الجديدة إلى القائمة
                self.points.append(point)
                if len(self.points) > self.max_points:
                    self.points.pop(0)  # إزالة أقدم نقطة إذا تجاوزت القائمة الحد الأقصى

                # تحديث الكاش بالنقاط الجديدة
                cache.set(self.status_key, self.points)

                # إرسال النقطة الجديدة للعميل مباشرة
                await self.send_to_web_page(point)

            except websockets.ConnectionClosed:
                print("Connection to the external WebSocket closed")
                break
            except Exception as e:
                print(f"An error occurred while receiving: {e}")
                break

    async def send_to_web_page(self, point):
        try:
            # إرسال الرسالة للصفحة الويب
            await self.send(text_data=json.dumps({'message': point}))
        except Exception as e:
            print(f"An error occurred while sending: {e}")

    async def send_message(self, event):
        point = event['message']
        await self.send(text_data=json.dumps({'message': point}))
