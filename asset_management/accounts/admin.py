from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AccessLevel, SystemAccessPermission
from mptt.admin import MPTTModelAdmin


@admin.register(AccessLevel)
class AccessLevelAdmin(MPTTModelAdmin):
    list_display = ('level_name', 'parent', 'main_level')
    mptt_indent_field = "level_name" 


@admin.register(SystemAccessPermission)
class SystemAccessPermissionAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
   
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('access_level', 'gender', 'phone_number', 'address', 'ip_login')}),
    )
   
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'access_level')