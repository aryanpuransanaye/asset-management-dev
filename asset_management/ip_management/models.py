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
        ('data-and-information', 'داده و اطلاعات'),
        ('software', 'نرم افزار'),
        ('services', 'سرویس'),
        ('hardware', 'سخت افزار'),
        ('places-and-areas', 'اماکن و محوطه'),
        ('human-resource', 'منابع انسانی'),
        ('infrastructure-asset', 'دارایی های زیر ساخت'),
        ('intangible-asset', 'دارایی های نامشهود'),
        ('supplier', 'تامین کنندگان'),
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
    

class ScanHistory(models.Model):

    STATUS_CHOICES = [
        ('running', 'در حال اجرا'),
        ('finished', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('no_new_ip', 'ip جدیدی یافت نشد'),
        ('canceled', 'کنسل شده'),
    ]

    network_range = models.ForeignKey(
        IPManage, 
        on_delete=models.CASCADE, 
        related_name='scan_history', 
        null=True, 
        blank=True, 
        verbose_name='محدوده شبکه'
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running', verbose_name='وضعیت')
    result_count = models.IntegerField(default=0, verbose_name="تعداد یافته‌ها")
    created_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ ایجاد')
    finished_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ پایان')
    error_message = models.TextField(blank=True, null=True, verbose_name="پیام خطا")