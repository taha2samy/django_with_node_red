from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from node_red.models import Element, ElementPermissionsGroup, ElementPermissionsUser
import orjson  # Replace json with orjson
from django.core.cache import cache
from collections import deque


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
        except Element.DoesNotExist:
            return [None, None]

    async def receive(self, text_data):
        try:
            data = orjson.loads(text_data)

            if data["type"] == "subscribe":
                # check if the user has permission to access the element and subscribe to it
                l = await self.get_permissions(self.user, data["element_id"])

                permission = l[0]
                element = l[1]
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
                        "permissions": permission.permissions
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
                        await self.send(text_data=orjson.dumps({"ss":data}).decode("utf-8"))
                        # if user has read and write permission, they can send and receive messages
                        await self.channel_layer.group_send(
                            data["element_id"],
                            {
                                "type": "message_element",
                                "element_id": data["element_id"],
                                "message": data["message"],
                                "channel": str(self.channel_name)
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
            await self.send(text_data=orjson.dumps({
                "type": "error",
                "error": str(e)
            }).decode("utf-8"))
            pass

    async def message_element(self, message):
        if self.channel_name != message["channel"]:
            await self.send(text_data=orjson.dumps(message).decode("utf-8"))

    async def permissions_updates(self, event):
        if event["state"] == "update" or event["state"] == "create":
            l = await self.get_permissions(self.user, event["message"]["element"])
            permission = l[0]
            element = l[1]
            
            if permission is not None:
                
                self.groups.update({str(event["message"]["element"]): permission.permissions})
                channel_of_permission= f"{permission.id}{permission._meta.model_name}"
                if channel_of_permission not in self.groups.keys():
                    print("channel_of_permission",channel_of_permission)
                    await self.channel_layer.group_add(channel_of_permission, self.channel_name)
                    self.groups.update({channel_of_permission:permission.permissions})
                    self.groups.pop(event["channel"])
                    await self.channel_layer.group_discard(str(event["channel"]), self.channel_name)
            else:
                # remove yourself from the group
                self.groups.pop(event["message"]["element"], None)
                self.groups.pop(event["channel"], None)

                await self.channel_layer.group_discard(str(event["message"]["element"]), self.channel_name)
                await self.channel_layer.group_discard(str(event["channel"]), self.channel_name)
                await self.send(text_data=orjson.dumps({
                    "type": "unsubscribe",
                    "element_id": event["message"]["element"]
                }).decode("utf-8"))
               

        elif event["state"] == "delete":
            l = await self.get_permissions(self.user, event["message"]["element"])
            permission = l[0]
            element = l[1]
            
            if permission is not None:
                self.groups.update({str(event["message"]["element"]): permission.permissions})
                channel_of_permission= f"{permission.id}{permission._meta.model_name}"
                if channel_of_permission in self.groups.keys():
                    self.channel_layer.group_add(channel_of_permission, self.channel_name)
                    self.groups.update({channel_of_permission:permission.permissions})
                    self.groups.pop(event["channel"])
                    await self.channel_layer.group_discard(str(event["channel"]), self.channel_name)
            else:
                self.groups.pop(event["message"]["element"], None)
                self.groups.pop(event["channel"], None)
                await self.channel_layer.group_discard(str(event["message"]["element"]), self.channel_name)
                await self.channel_layer.group_discard(str(event["channel"]), self.channel_name)
                await self.send(text_data=orjson.dumps({
                    "type": "unsubscribe",
                    "element_id": event["message"]["element"]
                }).decode("utf-8"))
                
        pass