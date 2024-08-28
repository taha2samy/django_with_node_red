from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User, Group

# Define choices for devices and status permissions
DEVICE_CHOICES = [
    ('Slider', 'Slider'),
    ('Toggle Button', 'Toggle Button'),
    ('Push Button', 'Push Button'),
    ('Series', 'Series'),
]

STATUS_CHOICES = [
    ('R', 'Read'),
    ('RC', 'Read and change'),
]

class Devices(models.Model):
    """Model representing a device with specific attributes."""

    name = models.CharField(
        max_length=50,
        choices=DEVICE_CHOICES,
        null=True,
        blank=True
    )
    device_id = models.CharField(max_length=50, primary_key=True)
    points = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1000)
        ]
    )
    description = models.TextField()

    def __str__(self) -> str:
        return f"{self.device_id}: {self.name}"

class PermissionManager(models.Manager):
    """Custom manager for handling permission logic for users and groups."""

    def has_permission(self, user, device):
        """
        Check if the user has direct permission for the device.
        If not, check if the user's groups have permission.
        """
        # Check for direct user permission
        device_permission = DevicesPermissionsUser.objects.filter(user=user, device=device).first()
        if device_permission:
            return device_permission.permissions

        # Check for group permission
        user_groups = user.groups.all()
        group_permission = DevicesPermissionsGroup.objects.filter(group__in=user_groups, device=device).first()
        if group_permission:
            return group_permission.permissions

        return None

    def has_user_permission_bygroup(self, user, device):
        """
        Check if the user's groups have permission for the device.
        """
        user_groups = user.groups.all()
        group_permission = DevicesPermissionsGroup.objects.filter(group__in=user_groups, device=device).first()
        if group_permission:
            return group_permission.permissions
        return None

class DevicesPermissionsUser(models.Model):
    """Model to represent user permissions for specific devices."""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(Devices, on_delete=models.CASCADE)
    permissions = models.CharField(max_length=2, choices=STATUS_CHOICES)

    # Default and custom managers
    objects = models.Manager()  # Default manager
    permission_manager = PermissionManager()  # Custom permission manager

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'device'], name='unique_user_device')
        ]

    def __str__(self) -> str:
        return f"{self.user} has permission {self.permissions} on {self.device}"

class DevicesPermissionsGroup(models.Model):
    """Model to represent group permissions for specific devices."""

    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    device = models.ForeignKey(Devices, on_delete=models.CASCADE)
    permissions = models.CharField(max_length=2, choices=STATUS_CHOICES)

    # Default and custom managers
    objects = models.Manager()  # Default manager
    permission_manager = PermissionManager()  # Custom permission manager

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'device'], name='unique_group_device')
        ]

    def __str__(self):
        return f'{self.group} has permission {self.permissions} on {self.device}'
