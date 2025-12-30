from django.db import models
from core.models import BaseAsset


class InfrastructureAssets(BaseAsset):
     
    supplier = models.CharField(max_length=500, null=True, blank=True, verbose_name='تأمین‌کننده / پیمانکار')
    location = models.CharField(max_length=500, null=True, blank=True, verbose_name='محل استقرار / موقعیت فیزیکی')
    related_property = models.CharField(max_length=500, null=True, blank=True, verbose_name='اموال مرتبط / شماره برچسب')
    usage = models.CharField(max_length=500, null=True, blank=True, verbose_name='نوع کاربری / مورد مصرف')
    owner = models.CharField(max_length=500, null=True, blank=True, verbose_name='مالک / مسئول نگهداری')
    name = models.CharField(max_length=500, null=True, blank=True, verbose_name='نام دارایی زیرساختی')
