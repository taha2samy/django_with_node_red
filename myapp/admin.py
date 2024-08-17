from django.contrib import admin
from .models import Devices

# Register the Devices model with the default admin site
class DevicesAdmin(admin.ModelAdmin):
    list_display = ('name', 'Device_id', 'points', 'description')  # Fields to display in the list view
    search_fields = ('name', 'Device_id')  # Fields to search by

admin.site.register(Devices, DevicesAdmin)
