from django.db import models
from accounts.models import User, AccessLevel

class IPManage(models.Model):

    SUBNET = [(str(i), str(i)) for i in range(33)]

    subnet = models.CharField(max_length=4, choices=SUBNET, verbose_name='ساب‌نت (Subnet)')
    name = models.CharField(max_length=50, verbose_name='نام محدوده')    
    ipaddress = models.GenericIPAddressField(verbose_name='آدرس IP')
    vlan = models.IntegerField(null=True, blank=True, verbose_name='وی‌لن (VLAN)')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر ثبت‌کننده')
    access_level = models.ForeignKey(AccessLevel, on_delete=models.CASCADE, verbose_name='سطح دسترسی')
    created_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ ایجاد')

    def __str__(self):
        return str(self.name)

    
class DiscoveredAsset(models.Model):
    CATEGORY_CHOICES = [
        ('0', 'داده و اطلاعات'),
        ('1', 'نرم افزار'),
        ('2', 'سرویس'),
        ('3', 'سخت افزار'),
        ('4', 'اماکن و محوطه'),
        ('5', 'منابع انسانی'),
        ('6', 'دارایی های زیر ساخت'),
        ('7', 'دارایی های نامشهود'),
        ('8', 'تامین کنندگان'),
    ]

    network_range = models.ForeignKey(
        IPManage, 
        on_delete=models.CASCADE, 
        related_name='dicovered_aasets', 
        null=True, 
        blank=True, 
        verbose_name='محدوده شبکه'
    )
    
    ipaddress = models.GenericIPAddressField(null=True, blank=True, verbose_name='آدرس IP')
    mac = models.CharField(max_length=20, null=True, blank=True, verbose_name='آدرس MAC')
    os = models.CharField(max_length=500, null=True, blank=True, verbose_name='سیستم عامل')
    vendor = models.CharField(max_length=500, null=True, blank=True, verbose_name='تولیدکننده')
    category = models.CharField(max_length=250, choices=CATEGORY_CHOICES, null=True, blank=True, default='بدون دسته بندی', verbose_name='دسته دارایی')
    access_level = models.ForeignKey(AccessLevel, on_delete=models.CASCADE, verbose_name='سطح دسترسی')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    created_at = models.DateTimeField(auto_now=True, verbose_name='زمان شناسایی')

    def __str__(self):
        return f"{self.ipaddress} - {self.vendor or 'Unknown'}"