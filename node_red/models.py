from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User, Group
import jwt
from datetime import datetime, timedelta
from django.conf import settings
import uuid
# Define choices for devices and status permissions



STATUS_CHOICES = [
    ('R', 'Read'),
    ('RC', 'Read and change'),
]

class Device(models.Model):
    """Model representing a device with specific attributes."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid5(uuid.NAMESPACE_DNS, 'Device'), editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField()
    token = models.CharField(max_length=1000, blank=True, null=True)
    def generate_jwt(self):
        """Generate a JWT for the device."""
        payload = {
            'id': str(self.id),
            'exp': datetime.utcnow() + timedelta(hours=15), 
            'iat': datetime.utcnow(),  
        }
        token = jwt.encode(payload, settings.SIMPLE_JWT['SIGNING_KEY'], algorithm=settings.SIMPLE_JWT['ALGORITHM'])
        return token
    def save(self, *args, **kwargs):
        """Override the save method to generate a token if not provided."""
        if not self.token:
            self.token = self.generate_jwt()
        super().save(*args, **kwargs)
    def __str__(self) -> str:
        return self.name
        pass
class Element(models.Model):
    """Model representing an element with specific attributes."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid5(uuid.NAMESPACE_DNS, 'element'), editable=False)
    name = models.CharField(max_length=50)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    element_id = models.CharField(max_length=50,unique=True)
    points = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    description = models.TextField()

    def __str__(self) -> str:
        return f"{self.element_id}: {self.name}"

class PermissionManager(models.Manager):
    """Custom manager for handling permission logic for users and groups."""

    def has_permission(self, user, element):
        """
        Check if the user has direct permission for the element.
        If not, check if the user's groups have permission.
        """
        # Check for direct user permission
        element_permission = ElementPermissionsUser.objects.filter(user=user, element=element).first()
        if element_permission:
            return element_permission.permissions

        # Check for group permission
        user_groups = user.groups.all()
        group_permission = ElementPermissionsGroup.objects.filter(group__in=user_groups, element=element).first()
        if group_permission:
            return group_permission.permissions

        return None

    def has_user_permission_bygroup(self, user, element):
        """
        Check if the user's groups have permission for the element.
        """
        user_groups = user.groups.all()
        group_permission = ElementPermissionsGroup.objects.filter(group__in=user_groups, element=element).first()
        if group_permission:
            return group_permission.permissions
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