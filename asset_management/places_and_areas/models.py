from django.db import models
from core.models import BaseAsset


class PlacesAndArea(BaseAsset):

    
    location = models.CharField(max_length=500, null=True, blank=True, verbose_name='محل استقرار / موقعیت')
    usage = models.CharField(max_length=500, null=True, blank=True, verbose_name='مورد مصرف / کاربرد')
    owner = models.CharField(max_length=500, null=True, blank=True, verbose_name='مالک / مسئول')
    name = models.CharField(max_length=500, null=True, blank=True, verbose_name='نام دارایی / تجهیزات')

