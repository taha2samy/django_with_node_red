from django.contrib import admin
from .models import Device, Element, ElementPermissionsUser, ElementPermissionsGroup,Connections

# Register Device model to the admin panel
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'token')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'token')

admin.site.register(Device, DeviceAdmin)
# Register Connections model to the admin panel
class ConnectionsAdmin(admin.ModelAdmin):
    list_display = ('id','device')
    pass
admin.site.register(Connections, ConnectionsAdmin)
# Register Element model to the admin panel
class ElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'element_id', 'points', 'description')
    search_fields = ('name', 'element_id')
    list_filter = ('points',)

admin.site.register(Element, ElementAdmin)

# Register ElementPermissionsUser model to the admin panel
class ElementPermissionsUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'element', 'permissions')
    search_fields = ('user__username', 'element__name')
    list_filter = ('permissions',)

admin.site.register(ElementPermissionsUser, ElementPermissionsUserAdmin)

# Register ElementPermissionsGroup model to the admin panel
class ElementPermissionsGroupAdmin(admin.ModelAdmin):
    list_display = ('group', 'element', 'permissions')
    search_fields = ('group__name', 'element__name')
    list_filter = ('permissions',)

admin.site.register(ElementPermissionsGroup, ElementPermissionsGroupAdmin)
