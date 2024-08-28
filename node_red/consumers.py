
from myproject.settings import NODE_RED_WEBSOCKET_URI
import json
import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import websockets
from django.core.cache import cache
from node_red.models import Devices, DevicesPermissionsUser

class BaseWebSocketConsumer(AsyncWebsocketConsumer):
    url_external = None  # Set the actual URL for external WebSocket connection
    max_messages = None  # Maximum number of messages to store
    last_messages = []  # Store last messages in memory
    is_connected = False
    async def connect(self):
        """
        Handle the connection to the WebSocket. 
        It retrieves the device associated with the group_id, checks user permissions,
        and connects to the external WebSocket if permissions are granted.
        """
        
        self.group_name = self.scope['url_route']['kwargs'].get('group_id')
        self.user = self.scope["user"]
        await self.accept()
        device = await self.get_device(self.group_name)  # Retrieve the device by ID
        if not device:
            await self.send_error("Device not found.")  # Send error if device does not exist
            
            return
        
        self.has_permission = await self.check_permission(device)  # Check if the user has permission
        if not self.has_permission:
            await self.send_error("Unauthorized Access")  # Send error if permission is denied
            return
        
        self.max_messages = device.points  # Set maximum messages based on device points
        await self.connect_external_ws()  # Connect to the external WebSocket
        await self.channel_layer.group_add(self.group_name, self.channel_name)  # Join the group
        await self.send_last_messages()  # Send any previously cached messages to the user
        self.is_connected = True
    async def disconnect(self, close_code):
        """
        Handle the disconnection from the WebSocket.
        It ensures the user is removed from the group and cancels any ongoing external WebSocket tasks.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)  # Remove user from group
        await self.cancel_external_ws_task()  # Cancel the external WebSocket task if it exists

    async def receive(self, text_data):
        """
        Handle incoming messages from the WebSocket.
        Depending on the user's permissions, it either processes the message or sends an unauthorized response.
        """
        if self.has_permission == "RC":  # Check if the user has read/change permissions
            await self.handle_authorized_message(text_data)  # Process the message if authorized
        else:
            await self.send_unauthorized_message()  # Send a message indicating lack of permission

    async def handle_authorized_message(self, text_data):
        """
        Process a message when the user has authorized permissions.
        It adds necessary information to the message and sends it to the external WebSocket.
        """
        message = json.loads(text_data)  # Parse the incoming message
        message.update({
            "group_id": self.group_name,  # Add group ID to the message
            "user": str(self.user),  # Include the user's information
            "Permissions": str(self.has_permission),  # Include the user's permissions
        })
        await self.send_to_external_ws(message)  # Send the message to the external WebSocket

    async def send_unauthorized_message(self):
        """
        Send messages from the cache to the user indicating that they do not have permission to access.
        Each message will include a permission indicator and an observation note.
        """
        last_messages = cache.get(self.group_name, [])  # Retrieve cached messages for the group
        for message in last_messages:
            message.update({"Permissions": "R", "observation": "You do not have permission to access"})  # Update message
            await self.send(text_data=json.dumps({'message': message}))  # Send the updated message

    async def receive_from_external_ws(self):
        """
        Continuously listen for messages from the external WebSocket.
        When a message is received, it checks if it belongs to the current group and handles it accordingly.
        """
        while True:
            try:
                message = json.loads(await self.websocket.recv())  # Receive message from external WebSocket
                message["is_disconnected"] = False  # Mark message as connected
                if message["group_id"] == self.group_name:  # Check if the message is for this group
                    await self.handle_message(message)  # Handle the message
            except websockets.ConnectionClosed:  # Handle connection closed exception
                await self.handle_disconnection()  # Attempt to reconnect
            except Exception:
                break  # Break loop on any other exception

    async def handle_disconnection(self):
        """
        Handle reconnection attempts if the external WebSocket disconnects.
        It sends a message to the user indicating the disconnection and attempts to reconnect.
        """
        reconnection_attempts = 0  # Initialize reconnection attempts
        while True:
            try:
                reconnection_attempts += 1  # Increment reconnection attempts
                last_message = {
                    "is_disconnected": True,
                    "reconnection_attempts": reconnection_attempts,
                    "disconnected_at": datetime.now().isoformat() if reconnection_attempts == 1 else None
                }
                await self.send(text_data=json.dumps({'message': last_message}))  # Inform the user about disconnection
                await asyncio.sleep(5)  # Wait before attempting to reconnect
                await self.connect_external_ws()  # Try to reconnect to the external WebSocket
                break  # Exit loop on successful reconnection
            except Exception:
                pass  # Handle any exceptions silently and continue trying to reconnect

        # Update last message on reconnection
        last_message = {"is_disconnected": False}  # Prepare message to indicate reconnection
        message_cache = cache.get(self.group_name, [])  # Retrieve cached messages
        if message_cache:
            last_message.update(message_cache[-1])  # Add the last cached message to the response

        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'send_message', 'message': last_message}  # Send the reconnection message to the group
        )

    async def connect_external_ws(self):
        """
        Establish a connection to the external WebSocket.
        If successful, it starts listening for messages from the external WebSocket.
        """
        try:
            self.websocket = await websockets.connect(self.url_external)  # Connect to external WebSocket
            self.external_ws_task = asyncio.create_task(self.receive_from_external_ws())  # Start receiving messages
        except Exception:
            await self.handle_disconnection()  # Handle any connection errors

    async def send_to_external_ws(self, message):
        """
        Send a message to the external WebSocket.
        It handles connection errors gracefully, attempting to reconnect if the connection is closed.
        """
        try:
            if self.websocket and self.websocket.open:  # Check if the WebSocket is open
                await self.websocket.send(json.dumps(message))  # Send the message
        except websockets.ConnectionClosed:
            await self.handle_disconnection()  # Attempt to reconnect if the connection is closed
        except Exception:
            pass  # Silently handle any other exceptions

    async def send_message(self, event):
        """
        Send a message to the WebSocket client from the channel layer.
        This method is called when a message is broadcasted to the group.
        """
        await self.send(text_data=json.dumps({'message': event['message']}))  # Send the message to the client

    async def handle_message(self, message):
        """
        Process an incoming message from the external WebSocket.
        It adds permission information and broadcasts the message to the group.
        """
        message["Permissions"] = "R"  # Set the permission level for the message
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'send_message', 'message': message}  # Broadcast the message to the group
        )

    async def get_device(self, device_id):
        """
        Retrieve a device object based on its ID.
        Returns the device if found, or None if not found.
        """
        try:
            return await sync_to_async(Devices.objects.get)(device_id=device_id)  # Fetch device from the database
        except Devices.DoesNotExist:
            return None  # Return None if the device does not exist

    async def check_permission(self, device):
        """
        Check if the user has permission to access the specified device.
        Returns True if permission is granted, False otherwise.
        """
        try:
            return await sync_to_async(DevicesPermissionsUser.permission_manager.has_permission)(self.user, device)  # Check permissions
        except Exception:
            return None  # Return None if an error occurs

    async def send_last_messages(self):
        """
        Send any previously cached messages to the user upon connection.
        This helps in keeping the user informed with the last known state.
        """
        last_messages = cache.get(self.group_name, [])  # Retrieve cached messages for the group
        for message in last_messages:
            await self.send(text_data=json.dumps({'message': message}))  # Send each cached message to the user

    async def send_error(self, error_message):
        """
        Send an error message to the WebSocket client and close the connection.
        This is used for sending error messages when an issue occurs during connection or permission checks.
        """
        await self.send(text_data=json.dumps({'message': {"error": error_message}}))  # Send the error message
        await self.close(code=4000)  # Close the connection if there's an error

    async def cancel_external_ws_task(self):
        """
        Cancel any ongoing external WebSocket task and close the WebSocket connection.
        This is called during disconnection to ensure resources are properly released.
        """
        if hasattr(self, 'external_ws_task'):
            self.external_ws_task.cancel()  # Cancel the external WebSocket listening task
        if hasattr(self, 'websocket') and self.websocket:
            await self.websocket.close()  # Close the external WebSocket connection
        self.is_connected = False

class NodeRED(BaseWebSocketConsumer):
    url_external = NODE_RED_WEBSOCKET_URI
    pass
