from django.db import models
from core.models import BaseAsset


class Services(BaseAsset):

    hardware_location = models.CharField(max_length=500, null=True, blank=True, verbose_name='محل استقرار سخت‌افزار')
    owner = models.CharField(max_length=150, null=True, blank=True, verbose_name='مالک دارایی')
    port = models.IntegerField(null=True, blank=True, verbose_name='port')
    related_property = models.CharField(max_length=500, null=True, blank=True, verbose_name='اموال مرتبط/شماره اموال')
    build_number_os = models.CharField(max_length=550, null=True, blank=True, verbose_name='شماره ساخت سیستم‌عامل (Build Number)')
    name = models.CharField(max_length=500, null=True, blank=True, verbose_name='نام دستگاه/تجهیزات')