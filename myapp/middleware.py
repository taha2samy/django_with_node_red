# myapp/middleware.py

from channels.exceptions import DenyConnection

class WebSocketProtocolMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # تحقق من نوع الاتصال
        if scope['type'] == 'websocket':
            path = scope['path']
            allowed_paths = [
                '/ws/switch/',
                '/ws/button/',
                '/ws/mywebsocket/series'
            ]
            if path not in allowed_paths:
                # رفض الاتصال إذا لم يكن المسار مسموحًا
                await send({
                    'type': 'websocket.close',
                    'code': 4000
                })
                return
        await self.inner(scope, receive, send)
