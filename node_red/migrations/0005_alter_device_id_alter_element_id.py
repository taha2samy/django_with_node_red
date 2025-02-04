# Generated by Django 5.1.5 on 2025-01-24 22:35

import node_red.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('node_red', '0004_alter_element_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='id',
            field=models.UUIDField(default=node_red.models.generate_uuid_device, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='element',
            name='id',
            field=models.UUIDField(default=node_red.models.generate_uuid_element, editable=False, primary_key=True, serialize=False),
        ),
    ]
