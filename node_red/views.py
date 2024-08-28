
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
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def test_view(request):
    return render(request,'test.html')