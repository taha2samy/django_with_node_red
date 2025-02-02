import jwt
from channels.auth import BaseMiddleware
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from .models import Device, Element
from .serializers import DeviceSerializer, ElementSerializer
import datetime
import logging
from django.forms.models import model_to_dict
from django.db.models import QuerySet
import uuid
logger = logging.getLogger(__name__)
def model_to_dict_updates(instance_or_queryset):
    """
    Convert a model instance or queryset to a dictionary with all fields, including `id`.

    :param instance_or_queryset: A Django model instance or queryset
    :return: A dictionary or list of dictionaries
    """
    if isinstance(instance_or_queryset, QuerySet):
        return [model_to_dict_updates(instance) for instance in instance_or_queryset]
    
    # For a single instance, include all fields (including `id`)
    data = model_to_dict(instance_or_queryset)
    data['id'] = instance_or_queryset.id  # Ensure the `id` is included

    # Convert UUID fields to string
    for field, value in data.items():
        if isinstance(value, uuid.UUID):
            data[field] = str(value)
    
    return data

class AuthMiddlewareDevice(BaseMiddleware):
    """
    WebSocket middleware for authenticating devices or users via JWT.
    """

    async def __call__(self, scope, receive, send):
        token = None

        try:
            # Extract token from the headers
            for key, value in scope["headers"]:
                if key == b"authorization":
                    token = value.decode().split(" ")[1]  # Get the token after "Bearer"
        except Exception as e:
            logger.error(f"Error extracting token: {e}")
            return await self.close_connection(send)
        
        if token:
            device, elements = await self.authenticate_token(token)
            if device is None:
                return await self.close_connection(send)

            scope["device"] = device  # Attach the authenticated user/device to the scope
            scope['element'] = elements  # Attach the elements to the scope
        return await super().__call__(scope, receive, send)
    @database_sync_to_async
    def authenticate_token(self, token):
        """
        Authenticate the token and return device data and elements if valid.
        """
        try:
            # Decode the token
            payload = jwt.decode(token, settings.DEVICES_SETTING['SIGNING_KEY'], algorithms=[settings.DEVICES_SETTING['ALGORITHM']], options={"verify_exp": settings.DEVICES_SETTING['CHEACKLIFETIME']})
            device_id = payload['id']
            if settings.DEVICES_SETTING['CHEACKLIFETIME']:
                if (payload["exp"]-datetime.datetime.now().timestamp() < 0 ):
                    raise jwt.ExpiredSignatureError    
            device = Device.objects.get(id=device_id)
            if settings.DEVICES_SETTING['INDATABASE']:
                if device.token != token:
                    raise jwt.InvalidTokenError
            elements = Element.objects.filter(device_id=device_id)
            # Serialize the data and return serialized response
            device_data = model_to_dict_updates(device)
            elements_data = model_to_dict_updates(elements)
            return device_data, elements_data
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired.")
            return None, None  # Token expired
        except jwt.InvalidTokenError:
            logger.error("Invalid token.")
            return None, None  # Invalid token
        except Device.DoesNotExist:
            logger.error(f"No device found with ID: {payload.get('id')}")
            return None, None  # Device not found
        except Exception as e:
            logger.error(f"Error during token authentication: {e}")
            return None, None  # Any other error

    async def close_connection(self, send):
        """Helper function to close the WebSocket connection."""
        await send({"type": "websocket.close..................................."})
