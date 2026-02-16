from django.db import models
from django_jalali.db import models as jmodels
from accounts.models import AccessLevel,  User
class Organization(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    access_level = models.ForeignKey(AccessLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name="organization", verbose_name='سطح دسترسی')

    name = models.CharField(max_length=100, verbose_name='نام سازمان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='آدرس')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='شماره تماس')
    email = models.EmailField(blank=True, null=True, verbose_name='ایمیل')
    website = models.CharField(max_length=500, blank=True, null=True, verbose_name='وب‌سایت')
    created_at = jmodels.jDateField(auto_now_add=True, null=True, blank=True, verbose_name='زمان ایجاد')

    def __str__(self):
        return self.name

class SubOrganization(models.Model):
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name='سازمان بالادستی')
    name = models.CharField(max_length=100, verbose_name='نام واحد/زیرمجموعه')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='آدرس اختصاصی')
    created_at = jmodels.jDateField(auto_now_add=True, null=True, blank=True, verbose_name='زمان ایجاد')
   
    def __str__(self):
        return f"{self.name} ({self.organization.name})"