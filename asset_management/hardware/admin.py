from django.contrib import admin
from .models import Hardware
# Register your models here.

from django.contrib import admin
from .models import Hardware

@admin.register(Hardware)
class HardwareAdmin(admin.ModelAdmin):

    list_display = [
        'id', 'name', 'organization', 'sub_organization', 
        'hostname', 'ipaddress', 'hardware_type', 'status', 'created_at'
    ]

    list_filter = ['organization', 'hardware_type', 'status', 'manufacturer']


    search_fields = ['name', 'hostname', 'ipaddress', 'mac', 'serial_number']

    fieldsets = (
        ('اطلاعات سازمانی', {
            'fields': ('organization', 'sub_organization', 'user', 'access_level')
        }),
        ('مشخصات فنی', {
            'fields': ('name', 'hostname', 'hardware_type', 'model', 'manufacturer', 'vendor')
        }),
        ('شبکه و امنیت', {
            'fields': ('ipaddress', 'mac', 'port', 'network_id', 'status', 'hardening', 'vulner_status')
        }),
        ('سایر موارد', {
            'fields': ('supplier', 'created_at', 'updated_at')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    ordering = ['-id']