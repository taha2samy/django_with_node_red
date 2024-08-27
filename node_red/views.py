
# Create your views here.
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .models import Devices
from adrf.views import APIView
from asgiref.sync import sync_to_async
from adrf.decorators import api_view


class MyDataView(APIView):
    async def post(self, request):
        try:
            message = request.data
            last_messages =   cache.get(str(message["group_id"]), [])
            
            if not last_messages or message != last_messages[-1]:
                device = await Devices.objects.filter(Device_id=message['group_id']).afirst()
                max_messages = device.points
                
                if len(last_messages) >= max_messages:
                    last_messages.pop(0)  # Remove the oldest message
                
                last_messages.append(message)
                print(str(message["group_id"]))
                cache.set(str(message["group_id"]), last_messages, None)
               
            return Response({"message----------------": "Data received successfully!"}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        except Devices.DoesNotExist:
            return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

def test_view(request):
    return render(request,'test.html')