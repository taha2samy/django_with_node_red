# myapp/routing.py

from django.urls import path,re_path
from . import consumers


websocket_urlpatterns = [
    re_path(r'ws/switch/$', consumers.SwitchButton_1.as_asgi()),
    re_path(r'ws/somepath/$', consumers.SwitchButton_1.as_asgi()),
    re_path(r'ws/button/$', consumers.BaseButton_1.as_asgi()),
    re_path(r'ws/mywebsocket/series$', consumers.Series_1.as_asgi()),
    re_path(r'ws/mywebsocket/BaseSlider_1$', consumers.BaseSlider_1.as_asgi())
]
