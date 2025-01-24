import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from node_red.middleware import AuthMiddlewareDevice
from node_red.routing_devices import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareDevice(
        URLRouter(websocket_urlpatterns)
    ),
})
