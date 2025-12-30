from django.db import models
from core.models import BaseAsset


class Hardware(BaseAsset):
    
    supplier = models.CharField(max_length=500, null=True, blank=True, verbose_name='تامین‌کننده/پشتیبان')
    hardening = models.CharField(max_length=500, null=True, blank=True, verbose_name='وضعیت امن‌سازی')
    vulner_status = models.CharField(max_length=500, null=True, blank=True, verbose_name='وضعیت آسیب‌پذیری')
    status = models.CharField(max_length=500, null=True, blank=True, verbose_name='وضعیت عملیاتی')
    hostname = models.CharField(max_length=500, null=True, blank=True, verbose_name='نام میزبان')
    port = models.IntegerField(null=True, blank=True, verbose_name='شماره پورت')
    model = models.CharField(max_length=500, null=True, blank=True, verbose_name='مدل دستگاه')
    manufacturer = models.CharField(max_length=500, null=True, blank=True, verbose_name='سازنده/برند')
    hardware_type = models.CharField(max_length=500, null=True, blank=True, verbose_name='نوع سخت‌افزار')
    name = models.CharField(max_length=500, null=True, blank=True, verbose_name='نام سخت افزار')