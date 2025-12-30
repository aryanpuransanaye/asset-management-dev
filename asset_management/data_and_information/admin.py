from django.contrib import admin
from .models import DataAndInformation
# Register your models here.

@admin.register(DataAndInformation)
class DataAndInformationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DataAndInformation._meta.fields]
