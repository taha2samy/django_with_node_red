from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import Device,Element
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.forms.models import model_to_dict
from .serializers import DeviceSerializer,ElementSerializer
from django.core.cache import cache

@receiver(post_save, sender=Device)
def device_post_save(sender, instance, created, **kwargs):
    state="update"
    channel_layer = get_channel_layer()
    message = DeviceSerializer(instance).data
    async_to_sync(channel_layer.group_send)(
        str(instance.id),  # Replace with your group name
        {
            "type": "device_updates",
            "message": message,
            "state":state
        }
    )
@receiver(post_delete,sender=Device)
def device_post_delete(sender, instance,**kwargs):
    state="delete"
    message=DeviceSerializer(instance).data
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        str(instance.id),  # Replace with your group name
        {
            "type": "device_updates",
            "message": message,
            "state":state
        }
    )
    pass

@receiver(post_save,sender=Element)
def element_post_save(sender, instance, created, **kwargs):
    if created:
        state="create"
    else:
        state="update"
    channel_layer = get_channel_layer()
    message = ElementSerializer(instance).data
    async_to_sync(channel_layer.group_send)(
        str(message['device']), 
        {
            "type": "elements_updates",
            "message": message,
            "state":state
        }
    )
@receiver(post_delete,sender=Element)
def element_post_delete(sender,instance,**kwargs):
    state="delete"
    channel_layer = get_channel_layer()
    message=ElementSerializer(instance).data
    async_to_sync(channel_layer.group_send)(
        str(message['device']), 
        {
            "type": "elements_updates",
            "message": message,
            "state":state
        }
    )
    cache.delete(message["id"])
    pass

    