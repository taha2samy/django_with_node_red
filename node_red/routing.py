# myapp/routing.py

from django.urls import path,re_path
from . import consumers


websocket_urlpatterns = [
    re_path(r'ws/mywebsocket/(?P<group_id>\w+)/$', consumers.NodeRED.as_asgi())
    
]
