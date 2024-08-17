from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Devices(models.Model):
    DEVICE_CHOICES = [
        ('Slider', 'Slider'),
        ('Toggle Button', 'Toggle Button'),
        ('Push Button', 'Push Button'),
        ('Series', 'Series'),
    ]

    # استخدام الخيارات مع CharField
    name = models.CharField(
        max_length=50,
        choices=DEVICE_CHOICES,  # تعيين الخيارات هنا
        null=True,
        blank=True
    )
    Device_id=models.CharField(max_length=50,primary_key=True)
    points = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1000)
        ]
    )
    description = models.TextField()
