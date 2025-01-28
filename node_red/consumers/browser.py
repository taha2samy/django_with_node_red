from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from node_red.models import Element,ElementPermissionsGroup,ElementPermissionsUser
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BrowserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close()
        self.groups = set()
        await self.accept()
    async def disconnect(self, close_code):
        print(f"WebSocket disconnected: {close_code}")
    @staticmethod
    @database_sync_to_async
    def get_permissions(user, element_id):
        element = Element.objects.get(id=element_id)
        permission = ElementPermissionsUser.permission_manager.get_max_permission(user, element)
        return permission
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            await self.send(text_data=json.dumps({"type": "acklllllllllllll"}))
            if data["type"] == "subscribe":
                await self.send(text_data=json.dumps({"type": "99999999999999"}))
                permission = await self.get_permissions(self.user, data["element_id"])
                await self.send(text_data=json.dumps({"type": "wwwwwwwwwwwwwww"}))
                if permission is not None:
                    await self.send(text_data=json.dumps({"type": "subscribssssssssssssse", "element_id": data["element_id"]}))
                    await self.channel_layer.group_add(data["element_id"],self.channel_name)
                    
            
            else:
                await self.send(text_data=json.dumps({"type": "unsubscribe", "element_id": data["element_id"]}))
                print(f"Unknown message type: {data['type']}")
        except Exception as e:
            pass
    async def message_element(self, message):
        await self.send(text_data=json.dumps(message))