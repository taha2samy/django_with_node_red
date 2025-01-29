import orjson
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from collections import deque
from node_red.models import Connections
from channels.db import database_sync_to_async
import psutil
import socket
import asyncio
import uuid
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
        self.connection_id =await self.create_connection(self.device['id'], self.scope)
        



    async def disconnect(self, close_code):
        # This method is called when the WebSocket connection is closed
        # Leave all groups
        for element_id in self.elements_ids:
            await self.channel_layer.group_discard(element_id, self.channel_name)
        await self.channel_layer.group_discard(self.device['id'], self.channel_name)
        await self.remove_connection(self.connection_id)

    async def receive(self, text_data):
        try:
            # Using orjson for faster JSON deserialization
            text_data_json = orjson.loads(text_data)
            element_id = text_data_json['element_id']
            message = text_data_json['message']

            # Use dictionary lookup instead of iterating through the list
            if element_id in self.elements_ids:
                element_data = self.elements_data[element_id]
                
                cache_key = f"{element_id}cache"
                queue = cache.get(cache_key, deque(maxlen=element_data['points']))
                queue.append(message)
                cache.set(cache_key, queue,timeout=None)
        
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
                text_data=orjson.dumps(message
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
    

    @staticmethod
    @database_sync_to_async
    def create_connection(device_id, details):
        def get_network_interfaces():
            interfaces = []
            try:
                for name, addrs in psutil.net_if_addrs().items():
                    stats = psutil.net_if_stats().get(name)
                    if stats and stats.isup:
                        interface_info = {
                            'interface': name,
                            'mtu': stats.mtu,
                            'is_up': stats.isup,
                            'addresses': [addr.address for addr in addrs if addr.family == socket.AF_INET]
                        }
                        interfaces.append(interface_info)
            except Exception as e:
                print(f"Error getting network info: {e}")
            return interfaces

        def decode_bytes(obj):
            if isinstance(obj, bytes):
                return obj.decode('utf-8')
            elif isinstance(obj, uuid.UUID):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: decode_bytes(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [decode_bytes(item) for item in obj]
            else:
                return obj

        # جمع معلومات الشبكة
        network_info = {
            'host': {
                'hostname': socket.gethostname(),
                'ip_address': socket.gethostbyname(socket.gethostname()),
                'interfaces': get_network_interfaces()
            }
        }

        # معالجة التفاصيل الأصلية
        details_serializable = decode_bytes(details)
        
        # دمج معلومات الشبكة مع التفاصيل
        details_serializable['network'] = network_info

        connection = Connections.objects.create(
            device_id=device_id,
            details=details_serializable
        )
        return connection.id



  
    @staticmethod
    @database_sync_to_async
    def remove_connection(connection_id):
        try:
            connection = Connections.objects.get(id=connection_id)
            connection.delete()
        except Connections.DoesNotExist:
            pass
    async def close_connection(self, event):
        if event['connection_id']==self.connection_id:
            await self.remove_connection(self.connection_id)
            self.close()
        pass