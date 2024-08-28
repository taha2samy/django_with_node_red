import asyncio
import json
import websockets
from django.core.management.base import BaseCommand
from myproject.settings import API_KEY, NODE_RED_WEBSOCKET_URI
from django.core.cache import cache  # Import the cache system
from node_red.models import Devices


class WebSocketClient:
    """
    A WebSocket client that connects to an external WebSocket server,
    listens for messages, and caches them in Django's cache system.
    """
    def __init__(self, url_external):
        self.url_external = url_external  # External WebSocket URL
        self.message_queue = asyncio.Queue()  # Queue to hold incoming messages
        self.cached_message_count = 0  # Counter for cached messages

    async def connect(self):
        """
        Connect to the WebSocket server and handle reconnections on failure.
        """
        while True:
            try:
                async with websockets.connect(self.url_external) as websocket:
                    print("Successfully connected to WebSocket.")
                    await self.listen_for_messages(websocket)
            except (websockets.ConnectionClosed, OSError) as error:
                print(f"Connection lost: {error}. Retrying in 5 seconds...")
                await asyncio.sleep(5)  # Wait before reconnecting

    async def listen_for_messages(self, websocket):
        """
        Continuously listen for messages from the WebSocket server.
        """
        print("Listening for incoming messages...")
        while True:
            try:
                raw_message = await websocket.recv()  # Receive raw message
                await self.message_queue.put(raw_message)  # Add message to the queue
            except websockets.ConnectionClosed:
                print("WebSocket connection closed.")
                break
            except Exception as error:
                print(f"Error receiving message: {error}")
                break

    async def process_queue(self):
        """
        Process messages in the queue and cache them.
        """
        while True:
            raw_message = await self.message_queue.get()  # Get message from the queue
            await self.cache_websocket_message(raw_message)  # Cache the message
            self.message_queue.task_done()  # Mark the task as done

            # Print the current count of cached messages on the same line
            print(f"\rTotal cached messages: {self.cached_message_count}", end='')  # Use \r to overwrite the line

    async def cache_websocket_message(self, raw_message):
        """
        Cache the incoming WebSocket message if it meets specific conditions.
        """
        try:
            message = json.loads(raw_message)  # Parse the JSON message
            group_id = str(message["group_id"])  # Extract group ID

            # Retrieve the last messages for the group from the cache
            last_messages = cache.get(group_id, [])
            
            # Prevent duplicate messages
            if not last_messages or message != last_messages[-1]:
                device = await Devices.objects.filter(device_id=message['group_id']).afirst()  # Fetch device by ID
                max_messages = device.points if device else 0  # Get the maximum number of messages

                # Maintain the cache size
                if len(last_messages) >= max_messages:
                    last_messages.pop(0)  # Remove the oldest message

                last_messages.append(message)  # Add the new message to the cache
                cache.set(group_id, last_messages, None)  # Update the cache

                # Increment the cached message count
                self.cached_message_count += 1
            
        except Exception as error:
            print(f"Error caching message: {error}")  # Log any errors

class Command(BaseCommand):
    """
    Django management command to run the WebSocket client.
    """
    help = 'Runs the WebSocket client to connect and cache messages.'

    def handle(self, *args, **kwargs):
        client = WebSocketClient(NODE_RED_WEBSOCKET_URI)  # Instantiate the WebSocket client
        event_loop = asyncio.get_event_loop()  # Get the current event loop
        try:
            event_loop.run_until_complete(asyncio.gather(
                client.connect(),  # Connect to the WebSocket
                client.process_queue()  # Start processing the message queue
            ))
        except KeyboardInterrupt:
            print("\nWebSocket client stopped manually.")  # Add newline for a clean exit
        finally:
            event_loop.close()  # Close the event loop gracefully
