from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from node_red.models import Element, ElementPermissionsGroup, ElementPermissionsUser
import orjson  # Replace json with orjson
from django.core.cache import cache
from collections import deque
import traceback
import uuid

class BrowserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close(code=4000)
        self.groups = {}
        await self.accept()

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected: {close_code}")

    @staticmethod
    @database_sync_to_async
    def get_permissions(user, element_id):
        try:
            
            element = Element.objects.get(id=element_id)
            permission = ElementPermissionsUser.permission_manager.get_max_permission(user, element)
            return [permission, element]
        except:
            return [None, None]

    async def receive(self, text_data):
        
        try:
            data = orjson.loads(text_data)
       
            if data["type"] == "subscribe":
                # check if the user has permission to access the element and subscribe to it
                thissd = await self.get_permissions(self.user, data["element_id"])
                permission = thissd[0]
                element = thissd[1]
                if permission is not None:
                    # channel of element

                    await self.channel_layer.group_add(data["element_id"], self.channel_name)
                    self.groups.update({data["element_id"]: permission.permissions})
                    
                    # channel of element permission
                    channel_of_permission= f"{permission.id}{permission._meta.model_name}"
                    await self.channel_layer.group_add(channel_of_permission, self.channel_name)
                    self.groups.update({channel_of_permission:permission.permissions })

                   
                    # declare that the user has subscribed to the element
                    await self.send(text_data=orjson.dumps({
                        "type": "subscribe",
                        "element_id": data["element_id"],
                        "subscribed": True,
                        "permissions": permission.permissions,
                        "detalis": element.details,
                        "connected":await element.is_connected()
                    }).decode("utf-8"))
                    # get old points from cache for the element and send them to the user
                    old_points = list(cache.get(f"{data['element_id']}cache", deque(maxlen=element.points)))
                    for point in old_points:
                        
                        await self.send(text_data=orjson.dumps({
                            "type": "message_element",
                            "message": point,
                            "element_id": data["element_id"]
                        }).decode("utf-8"))


            elif data["type"] == "unsubscribe":
                # Unsubscribe from the element
                await self.channel_layer.group_discard(data["element_id"], self.channel_name)
                # Use orjson.dumps() and decode bytes to str
                await self.send(text_data=orjson.dumps({
                    "type": "unsubscribe",
                    "element_id": data["element_id"],
                    "unsubscribe":True
                }).decode("utf-8"))

            elif data["type"] == "message_element":
                if data["element_id"] in self.groups.keys():

                    if self.groups[data["element_id"]] == "RC":
                        # if user has read and write permission, they can send and receive messages

                        await self.channel_layer.group_send(
                            data["element_id"],
                            {
                                "type": "message_element",
                                "element_id": data["element_id"],
                                "message": data["message"],
                                "channel": str(self.channel_name),
                                "server":"django",
                                "user_id":self.user.id,
                                "user":self.user.username
                            }
                        )
                    elif self.groups[data["element_id"]] == "R":
                        # if user has read permission, they can only receive messages
                        await self.send(text_data=orjson.dumps({"type":"subscribe",
                                                                "error":"unauthorized access",
                                                                "description":"you have only read"}).decode("utf-8"))
                        
                        pass
                    else:
                        # if user has no permission, they can't send or receive messages
                        await self.send(text_data=orjson.dumps({"type":"subscribe",
                                                                "error":"unauthorized access",
                                                                "description":"you have no permission"}).decode("utf-8"))
                        pass
        except Exception as e:
            # if an error occurs, handle it here
            error_details = {
                "type": "error",
                "error": str(e),
                "details": traceback.format_exc()
            }
            await self.send(text_data=orjson.dumps(error_details).decode("utf-8"))
            
            pass

    async def message_element(self, message):
        if "server" in message and message["server"] == "django":
            return
        if self.channel_name != message["channel"]:
            await self.send(text_data=orjson.dumps(message).decode("utf-8"))

    async def permissions_updates(self, event):
        if event["state"] in ["update", "create"]:
            await self.handle_update_or_create(event)
        elif event["state"] == "delete":
            await self.handle_delete(event)

    async def handle_update_or_create(self, event):
        l = await self.get_permissions(self.user, event["message"]["element"])
        permission, element = l
        if permission is not None:
            await self.update_permissions(event, permission)
        else:
            await self.remove_from_groups(event)

    async def handle_delete(self, event):
        l = await self.get_permissions(self.user, event["message"]["element"])
        permission, element = l

        if permission is not None:
            await self.update_permissions(event, permission)
        else:
            await self.remove_from_groups(event)

    async def update_permissions(self, event, permission):
        element_id = str(event["message"]["element"])
        channel_of_permission = f"{permission.id}{permission._meta.model_name}"
        if self.groups.get(element_id) != permission.permissions:
            self.groups[element_id] = permission.permissions
            await self.send(text_data=orjson.dumps({
                "type": "subscribe",
                "element_id": event["message"]["element"],
                "subscribed": True,
                "permissions": permission.permissions
            }).decode("utf-8"))

        if channel_of_permission not in self.groups:
            await self.channel_layer.group_add(channel_of_permission, self.channel_name)
            self.groups[channel_of_permission] = permission.permissions
            self.groups.pop(event["channel"], None)
            await self.channel_layer.group_discard(event["channel"], self.channel_name)

    async def remove_from_groups(self, event):
        element_id = str(event["message"]["element"])
        self.groups.pop(element_id, None)
        self.groups.pop(event["channel"], None)

        await self.channel_layer.group_discard(element_id, self.channel_name)
        await self.channel_layer.group_discard(event["channel"], self.channel_name)
        await self.send(text_data=orjson.dumps({
            "type": "unsubscribe",
            "element_id": event["message"]["element"],
            "unsubscribe": True
        }).decode("utf-8"))
    
    async def check_connection_element(self, event):
        connection_status = event["status"] == "connected"
        await self.send(text_data=orjson.dumps(event).decode("utf-8"))


    
        pass