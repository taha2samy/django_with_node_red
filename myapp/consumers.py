
import asyncio
import json
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
from .exmples import BaseSwitchButton,BaseButton,Series
class SwitchButton_1(BaseSwitchButton):
    url_external = "ws://localhost:1880/ws/mywebsocket"
    group_name = "1011"
    status_key = "switch_button_status_111"
    id = 1
    pass
class BaseButton_1(BaseButton):
    url_external = "ws://localhost:1880/ws/mywebsocket/button"
    group_name = "700"
    status_key = "basebutton_1"
    id = 2
    pass
class Series_1(Series):
    url_external = "ws://localhost:1880/ws/mywebsocket/series"
    group_name = "3453"
    status_key = "basebutton_122"
    id = 3
    pass
