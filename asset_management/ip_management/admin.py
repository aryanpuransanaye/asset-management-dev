from django.contrib import admin
from .models import DiscoveredAsset, IPManage
# Register your models here.

@admin.register(DiscoveredAsset)
class DiscoveredAssetAdmin(admin.ModelAdmin):
    list_display = ['ipaddress', 'network_range', 'mac', 'os', 'vendor', 'category','access_level', 'user', 'created_at']

@admin.register(IPManage)
class IPManageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'ipaddress', 'subnet', 'vlan']