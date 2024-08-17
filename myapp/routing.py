# myapp/routing.py

from django.urls import path,re_path
from . import consumers


websocket_urlpatterns = [
    re_path(r'ws/somepath/$', consumers.ForbiddenConsumer.as_asgi()),
    re_path(r'ws/mywebsocket/BaseSlider_1/(?P<group_id>\w+)/$', consumers.test.as_asgi())
    
]
