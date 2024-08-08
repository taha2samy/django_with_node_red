from django.db import models

# Create your models here.
class Devices(models.Model):
    name=models.CharField(max_length=50, null=True, blank=True)
    group_name=models.CharField(max_length=30, null=True, blank=True)
    data_key=models.CharField(max_length=30, null=True, blank=True)
    external_url = models.CharField(max_length=200)
    description = models.TextField()
    routing_url=models.CharField(max_length=200,blank=True)