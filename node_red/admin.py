from django.contrib import admin
from .models import Devices,DevicesPermissionsUser,DevicesPermissionsGroup
@admin.register(Devices)
class DevicesAdmin(admin.ModelAdmin):
    list_display = ('name', 'Device_id', 'points', 'description')
    search_fields = ('name', 'Device_id')
    list_filter = ('name',)
class DevicesPermissionsUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'permissons')
    search_fields = ('user__username', 'device__name')
    list_filter = ('permissons',)

class DevicesPermissionsGroupAdmin(admin.ModelAdmin):
    list_display = ('group', 'device', 'permissons')
    search_fields = ('group__name', 'device__name')
    list_filter = ('permissons',)

admin.site.register(DevicesPermissionsUser, DevicesPermissionsUserAdmin)
admin.site.register(DevicesPermissionsGroup, DevicesPermissionsGroupAdmin)
