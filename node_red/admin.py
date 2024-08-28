from django.contrib import admin
from .models import Devices, DevicesPermissionsUser, DevicesPermissionsGroup

@admin.register(Devices)
class DevicesAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_id', 'points', 'description')
    search_fields = ('name', 'device_id')
    list_filter = ('name',)

@admin.register(DevicesPermissionsUser)
class DevicesPermissionsUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'permissions')
    search_fields = ('user__username', 'device__name')
    list_filter = ('permissions',)

@admin.register(DevicesPermissionsGroup)
class DevicesPermissionsGroupAdmin(admin.ModelAdmin):
    list_display = ('group', 'device', 'permissions')
    search_fields = ('group__name', 'device__name')
    list_filter = ('permissions',)
