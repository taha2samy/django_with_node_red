# pp.py
import asyncio
import json
import websockets
from django.apps import apps
from asgiref.sync import sync_to_async
from django.core.cache import cache

class ExternalWebSocketHandler:
    url_external = "ws://localhost:1880/ws/mywebsocket/test"  # غيّر إلى الـ URL الفعلي
    cache_time = 300  # مثال على مدة التخزين في الثانية
    reconnect_delay = 1  # التأخير بالثواني قبل محاولة إعادة الاتصال
    message_timeout = 20  # المهلة بالثواني قبل التحقق من الرسائل المفقودة

    def __init__(self):
        print("Initializing WebSocket Handler")
        self.websocket = None
        self.receive_task = None
        self.last_message_time = None  # تتبع وقت آخر رسالة مستلمة

    async def start(self):
        await self.connect()

    async def connect(self):
        print("Connecting to WebSocket...")
        self.websocket = await self.connect_external_ws()
        if self.websocket:
            print("Connected to WebSocket.")
            self.receive_task = asyncio.create_task(self.receive_from_external_ws())
        else:
            print("Failed to connect to WebSocket.")

    async def disconnect(self):
        if self.receive_task:
            self.receive_task.cancel()
        if self.websocket:
            await self.websocket.close()

    async def connect_external_ws(self):
        try:
            return await websockets.connect(self.url_external)
        except Exception as e:
            print(f"Connection error: {e}")
            return None

    async def receive_from_external_ws(self):
        print("Listening for messages...")
        while True:
            try:
                print("Waiting to receive a message...")
                raw_message = await asyncio.wait_for(self.websocket.recv(), timeout=self.message_timeout)
                print(f"Message received: {raw_message}")
                message = json.loads(raw_message)
                print(f"Parsed message: {message}")

                if not message:
                    print("Received empty message, continuing...")
                    continue

                await self.handle_message(message)
                self.last_message_time = asyncio.get_event_loop().time()  # تحديث وقت آخر رسالة

            except asyncio.TimeoutError:
                print("No message received for 2 seconds, trying to reconnect...")
                await self.reconnect()
                break
            except websockets.ConnectionClosed:
                print("WebSocket connection closed")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    async def reconnect(self):
        await self.disconnect()  # فصل الاتصال الحالي
        await asyncio.sleep(self.reconnect_delay)  # الانتظار قبل إعادة الاتصال
        await self.connect()  # محاولة إعادة الاتصال

    async def handle_message(self, message):
        device_id = message.get("group_id")
        print(f"Handling message for device_id: {device_id}")

        if not device_id:
            print("No device_id found in the message.")
            return

        Devices = apps.get_model('node_red', 'Devices')

        try:
            device = await sync_to_async(Devices.objects.get)(Device_id=device_id)
        except Devices.DoesNotExist:
            print(f"Device with ID {device_id} does not exist.")
            return
        
        last_messages = cache.get(device_id, [])
        
        if not last_messages or message != last_messages[-1]:
            if len(last_messages) >= device.points:
                last_messages.pop(0)
            
            last_messages.append(message)
            cache.set(device_id, last_messages, self.cache_time)

            print(f"Updated last messages for device_id {device_id}: {last_messages}")
