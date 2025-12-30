from django.db import models
from core.models import BaseAsset

# Create your models here.
class IntangibleAsset(BaseAsset):

    supplier = models.CharField(max_length=500, null=True, blank=True, verbose_name='تأمین‌کننده / فروشنده')
    location = models.CharField(max_length=500, null=True, blank=True, verbose_name='محل استقرار / موقعیت فیزیکی')
    usage = models.CharField(max_length=500, null=True, blank=True, verbose_name='نوع کاربری / مورد مصرف')
    owner = models.CharField(max_length=500, null=True, blank=True, verbose_name='مالک دارایی / مسئول')
    name = models.CharField(max_length=500, null=True, blank=True, verbose_name='نام دارایی / تجهیزات')