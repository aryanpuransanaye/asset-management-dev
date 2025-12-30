from django.db import models
from django_jalali.db import models as jmodels
from accounts.models import User, AccessLevel
from organization.models import Organization, SubOrganization




class BaseAsset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    access_level = models.ForeignKey(AccessLevel, on_delete=models.CASCADE, verbose_name='سطح دسترسی')
    ipaddress = models.CharField(max_length=15, null=True, blank=True, verbose_name='آدرس IP')
    mac = models.CharField(max_length=20, null=True, blank=True, verbose_name='آدرس MAC')
    os = models.CharField(max_length=500, null=True, blank=True, verbose_name='سیستم عامل')
    vendor = models.CharField(max_length=500, null=True, blank=True, verbose_name='تولیدکننده (Vendor)')
    organization = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name='سازمان')
    sub_organization = models.ForeignKey(SubOrganization, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name='زیرمجموعه')
    network_id = models.CharField(max_length=128, null=True, blank=True, default=0, verbose_name='شناسه شبکه')
    created_at = jmodels.jDateField(auto_now_add=True, null=True, blank=True, verbose_name='زمان ایجاد')
    updated_at = jmodels.jDateField(auto_now=True, verbose_name='زمان به‌روزرسانی')

    class Meta:
        abstract = True