from rest_framework import serializers
from .models import Device,Element,ElementPermissionsUser,ElementPermissionsGroup

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__' 

class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element
        fields = '__all__'

class ElementPermissionsUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementPermissionsUser
        fields = '__all__'

class ElementPermissionsGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementPermissionsGroup
        fields = '__all__'
