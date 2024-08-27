import asyncio
import json
import websockets
import aiohttp
from myproject.settings import API_KEY
class SimpleWebSocketClient:
    url_external = "ws://localhost:1880/ws/mywebsocket/test"  # Change to your actual WebSocket URL
    http_post_url = "http://localhost:8000/api/node_red/"  # Change to your actual HTTP endpoint

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

                # Send the message to the HTTP endpoint
                await self.send_to_http_endpoint(raw_message)

            except websockets.ConnectionClosed:
                print("WebSocket connection closed")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
    async def send_to_http_endpoint(self, raw_message):
        async with aiohttp.ClientSession() as session:
            json_data = json.loads(raw_message)
            headers = {
                'X-API-Key': API_KEY,  # استخدم المفتاح من الإعدادات
            }
            async with session.post(self.http_post_url, json=json_data, headers=headers) as response:
                if response.status == 200:
                   print(f"Failed to send message. Status: ")
                else:
                    print(f"Failed to send message. Status:")


def main():
    client = SimpleWebSocketClient()
    asyncio.run(client.connect())

if __name__ == "__main__":
    main()
