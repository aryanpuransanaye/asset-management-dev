from django.db import models
from core.models import BaseAsset

class Software(BaseAsset):
    
    LICENCE_STATUS = [
        ('a', 'فعال'),
        ('d', 'غیر فعال')
    ]

    supplier = models.CharField(max_length=500, verbose_name='تأمین‌کننده', null=True, blank=True)
    hardware_location = models.CharField(max_length=500, verbose_name='محل استقرار سخت‌افزار', null=True, blank=True)
    related_property = models.CharField(max_length=500, verbose_name='دارایی مرتبط', null=True, blank=True)
    port = models.IntegerField(verbose_name='پورت', null=True, blank=True)
    owner = models.CharField(max_length=150, verbose_name='مالک', null=True, blank=True)
    license_status = models.CharField(max_length=150, choices=LICENCE_STATUS, verbose_name='وضعیت لایسنس', null=True, blank=True)
    license_expired_date = models.CharField(max_length=150, verbose_name='تاریخ انقضای لایسنس', null=True, blank=True)
    manufacturer = models.CharField(max_length=150, verbose_name='سازنده', null=True, blank=True)
    name = models.CharField(max_length=500, verbose_name='نام نرم‌افزار', null=True, blank=True)
    
    