from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User, Group
import jwt
from datetime import datetime, timedelta
from django.conf import settings
import uuid
from channels.db import database_sync_to_async

# Define choices for devices and status permissions

def generate_uuid_device():
    return uuid.uuid5(uuid.NAMESPACE_DNS, 'Device'+str(uuid.uuid4()))
def generate_uuid_element():
    return uuid.uuid5(uuid.NAMESPACE_DNS, 'element'+str(uuid.uuid4()))
def generate_uuid_connection():
    return uuid.uuid5(uuid.NAMESPACE_DNS, 'device connection'+str(uuid.uuid4()))


STATUS_CHOICES = [
    ('R', 'Read'),
    ('RC', 'Read and change'),
]

class Device(models.Model):
    """Model representing a device with specific attributes."""
    id = models.UUIDField(primary_key=True, default=generate_uuid_device, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField()
    token = models.CharField(max_length=1000, blank=True, null=True)
    def generate_jwt(self):
        """Generate a JWT for the device."""
        payload = {
            'id': str(self.id),
            'exp': int((datetime.now() + settings.DEVICES_SETTING['LIFETIME']).timestamp()), 
            'iat': int(datetime.now().timestamp()),  
        }
        token = jwt.encode(payload, settings.DEVICES_SETTING['SIGNING_KEY'], algorithm=settings.DEVICES_SETTING['ALGORITHM'])
        return token
    def save(self, *args, **kwargs):
        """Override the save method to generate a token if not provided."""
        if not self.token:
            self.token = self.generate_jwt()
        super().save(*args, **kwargs)
    def __str__(self) -> str:
        return self.name
        
class Connections(models.Model):
    id = models.UUIDField(primary_key=True, default=generate_uuid_connection, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='connections')
    details = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Connection for device {self.device.name}"
    
 
class Element(models.Model):
    """Model representing an element with specific attributes."""
    id = models.UUIDField(primary_key=True, default=generate_uuid_element, editable=False)
    name = models.CharField(max_length=50)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    element_id = models.CharField(max_length=50, unique=True)
    points = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    description = models.TextField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @database_sync_to_async
    def is_connected(self):
        """Check if the element's device has any connections."""
        return Connections.objects.filter(device=self.device).exists()
       

    def __str__(self) -> str:
        return f"{self.element_id}: {self.name}"

class PermissionManager(models.Manager):
    """Custom manager for handling permission logic for users and groups."""

    def get_user_permission(self, user, element):
        """
        check if the user has permission for the element.
        """
        # Check for direct user permission
        element_permission = ElementPermissionsUser.objects.filter(user=user, element=element).first()
        if element_permission:
            return element_permission


        return None

    def get_max_group_permission(self,user,element):
        """
        Get the maximum permission for a group on an element.
        """
        groups = user.groups.all()
        element_permission = ElementPermissionsGroup.objects.filter(group__in=groups, element=element).order_by('permissions').last()
        if element_permission:
            return element_permission
        return None
    def get_max_permission(self, user, element):
        """
        Get the maximum permission for a user on an element.
        """
        user_permission = self.get_user_permission(user, element)
        group_permission = self.get_max_group_permission(user, element)

        if user_permission and user_permission.permissions == 'RC':
            return user_permission
        if group_permission and group_permission.permissions == 'RC':
            return group_permission
        if user_permission and user_permission.permissions == 'R':
            return user_permission
        if group_permission and group_permission.permissions == 'R':
            return group_permission

        return None
class ElementPermissionsUser(models.Model):
    """Model to represent user permissions for specific elements."""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    permissions = models.CharField(max_length=2, choices=STATUS_CHOICES)

    objects = models.Manager()  # Default manager
    permission_manager = PermissionManager()  # Custom permission manager

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'element'], name='unique_user_element')
        ]

    def __str__(self) -> str:
        return f"{self.user} has permission {self.permissions} on {self.element}"

class ElementPermissionsGroup(models.Model):
    """Model to represent group permissions for specific elements."""

    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    permissions = models.CharField(max_length=2, choices=STATUS_CHOICES)

    objects = models.Manager()  # Default manager
    permission_manager = PermissionManager()  # Custom permission manager

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'element'], name='unique_group_element')
        ]

    def __str__(self):
        return f'{self.group} has permission {self.permissions} on {self.element}'