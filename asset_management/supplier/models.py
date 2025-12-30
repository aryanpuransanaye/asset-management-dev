from django.db import models
from core.models import BaseAsset

class Supplier(BaseAsset):

    suppliers_name = models.CharField(max_length=500, null=True, blank=True, verbose_name='نام شرکت تأمین‌کننده')
    suppliers_location = models.CharField(max_length=500, null=True, blank=True, verbose_name='آدرس شرکت تأمین‌کننده')
    email = models.EmailField(max_length=500, null=True, blank=True, verbose_name='پست الکترونیک (ایمیل)')
    
    manager_name = models.CharField(max_length=500, null=True, blank=True, verbose_name='نام مدیر عامل / مسئول')
    manager_mobile_number = models.CharField(max_length=11, null=True, blank=True, verbose_name='شماره همراه مدیر')
    
    support_name = models.CharField(max_length=500, null=True, blank=True, verbose_name='نام کارشناس پشتیبانی')
    support_mobile_number = models.CharField(max_length=11, null=True, blank=True, verbose_name='شماره همراه پشتیبانی')
    
    company_mobile_number = models.CharField(max_length=11, null=True, blank=True, verbose_name='شماره تماس ثابت شرکت')
    related_property = models.CharField(max_length=500, null=True, blank=True, verbose_name='دارایی‌های مرتبط / شماره قرارداد')
