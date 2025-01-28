from django.urls import path
from node_red.consumers.browser import BrowserConsumer

websocket_urlpatterns_browser = [
    path("browser/simple/", BrowserConsumer.as_asgi()),
]
