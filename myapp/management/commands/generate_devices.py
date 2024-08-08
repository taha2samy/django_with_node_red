from django.core.management.base import BaseCommand
from myapp.models import Devices
import os

class Command(BaseCommand):
    help = 'Generate SwitchButton classes from Devices model'

    def handle(self, *args, **kwargs):
        # Path to the file where classes will be generated
        output_path = os.path.join('myapp', 'consumers.py')
        with open(output_path, 'w') as file:
            file.write('')
        # Fetch all device entries
        devices = Devices.objects.all()
        init ="""
import asyncio
import json
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
from .exmples import BaseSwitchButton"""
        new_classes = []

        for device in devices:
            class_name = f"SwitchButton_{device.id}"
            class_code = f"""
class {class_name}(BaseSwitchButton):
    url_external = "{device.external_url}"
    group_name = "{device.group_name}"
    status_key = "{device.data_key}"
    id = "{device.id}"
    pass
"""
            new_classes.append(class_code)

        if os.path.exists(output_path):
            # Read existing content
            with open(output_path, 'r') as file:
                lines = file.readlines()

            # Keep the first 20 lines
            first_part = lines[:20]

            # Create new content by combining the first part with the new class codes
            new_content = init+''.join(first_part) + ''.join(new_classes)
        else:
            # If file doesn't exist, just use the new class codes
            new_content = ''.join(new_classes)

        # Write the new content to the file

        with open(output_path, 'w') as file:
            file.write(new_content)

        self.stdout.write(self.style.SUCCESS(f'Generated classes and updated {output_path} number of devices {len(new_classes)}'))
