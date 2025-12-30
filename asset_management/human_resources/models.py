from django.db import models
from django_jalali.db import models as jmodels
from core.models import BaseAsset

class HumanResource(BaseAsset):

    full_name = models.CharField(max_length=500, null=True, blank=True, verbose_name='نام و نام خانوادگی')
    manager = models.CharField(max_length=500, null=True, blank=True, verbose_name='مدیر مستقیم')
    start_date = jmodels.jDateField(null=True, blank=True, verbose_name='تاریخ شروع به کار')
    end_date_of_work = jmodels.jDateField(null=True, blank=True, verbose_name='تاریخ پایان همکاری')
    organizational_unit = models.CharField(max_length=500, null=True, blank=True, verbose_name='واحد سازمانی')
    location = models.CharField(max_length=500, null=True, blank=True, verbose_name='محل استقرار / دفتر')
    administrative_position = models.CharField(max_length=500, null=True, blank=True, verbose_name='پست سازمانی / سمت')
    personnel_id = models.CharField(max_length=500, null=True, blank=True, verbose_name='شماره پرسنلی')