from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User, Group

class Devices(models.Model):
    DEVICE_CHOICES = [
        ('Slider', 'Slider'),
        ('Toggle Button', 'Toggle Button'),
        ('Push Button', 'Push Button'),
        ('Series', 'Series'),
    ]

    name = models.CharField(
        max_length=50,
        choices=DEVICE_CHOICES,
        null=True,
        blank=True
    )
    Device_id = models.CharField(max_length=50, primary_key=True)
    points = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1000)
        ]
    )
    description = models.TextField()
    def __str__(self) -> str:
        return f"{self.Device_id}:{self.name}"

class PermissionManager(models.Manager):
    def has_permission(self, user, device):
        device_permission = DevicesPermissions.objects.filter(user=user, device=device).first()
        if device_permission:
            return device_permission.permissons

        user_groups = user.groups.all()
        group_permission = GroupSettings.objects.filter(group__in=user_groups, device=device).first()
        if group_permission:
            return group_permission.permissons

        return None

    def has_user_permission_bygroup(self, user, device):
        user_groups = user.groups.all()
        group_permission = GroupSettings.objects.filter(group__in(user_groups), device=device).first()
        if group_permission:
            return group_permission.permissons
        return None
        
class DevicesPermissionsUser(models.Model):
    STATUS_CHOICES = [
        ('R', 'Read'),
        ('C', 'Change'),
        ('RC', 'Read and change'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    device = models.OneToOneField(Devices, on_delete=models.CASCADE)
    permissons = models.CharField(max_length=2, choices=STATUS_CHOICES)
    
    # مدراء الكائنات
    objects = models.Manager()  # المدير الافتراضي
    permission_manager = PermissionManager()  # المدير المخصص
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'device'], name='unique_user_device')
        ]
    def __str__(self) -> str:
        return f"{self.user} has permission {self.permissons}"
class DevicesPermissionsGroup(models.Model):
    STATUS_CHOICES = [
        ('R', 'Read'),
        ('C', 'Change'),
        ('RC', 'Read and change'),
    ]
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    device = models.OneToOneField(Devices, on_delete=models.CASCADE)
    permissons = models.CharField(max_length=2, choices=STATUS_CHOICES)
    
    # مدراء الكائنات
    objects = models.Manager()  # المدير الافتراضي
    permission_manager = PermissionManager()  # المدير المخصص

    def __str__(self):
        return f'Settings for {self.group.name} on {self.device.name}'
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'device'], name='unique_group_device')
        ]

