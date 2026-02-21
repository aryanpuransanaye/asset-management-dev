# active_directory/admin.py
from django.contrib import admin
from .models import ActiveDirectory

@admin.register(ActiveDirectory)
class ActiveDirectoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'server_address', 'domain_name', 'username', 'port', 'search_base', 'created_at')
    search_fields = ('server_address', 'domain_name', 'username')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25