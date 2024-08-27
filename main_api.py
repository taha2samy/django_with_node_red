import asyncio
import json
import websockets
import aiohttp
from aiohttp import ClientSession
from myproject.settings import API_KEY

class SimpleWebSocketClient:
    url_external = "ws://localhost:1880/ws/mywebsocket/test"  # Change to your actual WebSocket URL
    http_post_url = "http://localhost:8000/api/node_red/"  # Change to your actual HTTP endpoint

    def __init__(self):
        self.session = None
        self.queue = asyncio.Queue()

    async def connect(self):
        async with websockets.connect(self.url_external) as websocket:
            print("Connected to WebSocket.")
            await self.listen_for_messages(websocket)

    async def listen_for_messages(self, websocket):
        print("Listening for messages...")
        while True:
            try:
                raw_message = await websocket.recv()
                message = json.loads(raw_message)
                print(f"Received message: {message}")

                # Add the message to the queue for processing
                await self.queue.put(raw_message)

            except websockets.ConnectionClosed:
                print("WebSocket connection closed")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    async def process_queue(self):
        while True:
            raw_message = await self.queue.get()
            await self.send_to_http_endpoint(raw_message)
            self.queue.task_done()

    async def send_to_http_endpoint(self, raw_message):
        if not self.session:
            self.session = ClientSession()

        json_data = json.loads(raw_message)
        headers = {
            'X-API-Key': API_KEY,  # استخدم المفتاح من الإعدادات
        }
        try:
            async with self.session.post(self.http_post_url, json=json_data, headers=headers) as response:
                if response.status == 200:
                    print(f"Message sent successfully: {json_data}")
                else:
                    print(f"Failed to send message. Status: {response.status}")
        except Exception as e:
            print(f"Error sending message: {e}")

    async def close_session(self):
        if self.session:
            await self.session.close()

def main():
    client = SimpleWebSocketClient()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asyncio.gather(
            client.connect(),
            client.process_queue()
        ))
    except KeyboardInterrupt:
        print("Client stopped manually.")
    finally:
        loop.run_until_complete(client.close_session())

if __name__ == "__main__":
    main()
