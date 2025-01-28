import orjson
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from collections import deque
import asyncio

class NodeRed(AsyncWebsocketConsumer):
    """
    Node Red consumer
    """

    async def connect(self):
        # This method is called when a WebSocket connection is requested
        self.device = self.scope.get('device')
        elements = self.scope.get('element')
        if elements is not None:
            self.elements_data = {e['id']: e for e in elements}
            self.elements_ids = set(self.elements_data.keys())
        else:
            self.elements_data = {}
            self.elements_ids = set()

        print(f"Connected to device: {self.scope['path']}")
        await asyncio.gather(
            *(self.channel_layer.group_add(e_id, self.channel_name) for e_id in self.elements_ids),
            self.channel_layer.group_add(self.device['id'], self.channel_name)
        )

        await self.accept()



    async def disconnect(self, close_code):
        # This method is called when the WebSocket connection is closed
        # Leave all groups
        for element_id in self.elements_ids:
            await self.channel_layer.group_discard(element_id, self.channel_name)
        await self.channel_layer.group_discard(self.device['id'], self.channel_name)

    async def receive(self, text_data):
        try:
            # Using orjson for faster JSON deserialization
            text_data_json = orjson.loads(text_data)
            element_id = text_data_json['id_element']
            message = text_data_json['message']

            # Use dictionary lookup instead of iterating through the list
            if element_id in self.elements_ids:
                element_data = self.elements_data[element_id]
                
                cache_key = f"{element_id}cache"
                queue = cache.get(cache_key, deque(maxlen=element_data['points']))
                queue.append(message)
                cache.set(cache_key, queue)
        
                await self.channel_layer.group_send(
                    element_id,
                    {
                        'type': 'message_element',
                        'id_element': element_id,
                        'message': message,
                        'channel': str(self.channel_name),
                    }
                )
        except Exception as e:
            # Handle exception (consider logging it for debugging)
            pass

    async def message_element(self, message):
        if message['channel'] != self.channel_name:
            await self.send(
                text_data=orjson.dumps(
                    {
                        "id_element": message['id_element'],
                        "message": message["message"],
                    }
                ).decode('utf-8')  # Decode to string for WebSocket transmission
            )
    async def device_updates(self,event):
        if event['state']=="update":
            self.device=event["message"]
            pass
        
        elif event['state']=="delete":
            await self.close()
            
        else:
            pass
    async def elements_updates(self,event):
        if event["state"]=="create":
            await self.channel_layer.group_add( event['message']["id"], self.channel_name)
            self.elements_ids.add(event['message']["id"])
            self.elements_data[event['message']["id"]]=event["message"]
            pass
        elif event["state"]=="update":
            self.elements_data[event['message']["id"]]=event["message"]
            pass
        elif event["state"]=="delete":
            await self.channel_layer.group_discard( event['message']["id"], self.channel_name)
            self.elements_ids.discard(event['message']["id"])
            del self.elements_data[event['message']["id"]]
            pass
        pass