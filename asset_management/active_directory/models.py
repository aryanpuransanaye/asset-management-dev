from django.db import models
from django_jalali.db import models as jmodels

class ActiveDirectory(models.Model) :

    server_address = models.CharField(max_length=50,null=False,blank=False, verbose_name="آدرس سرور")
    domain_name = models.CharField(max_length=50,null=False,blank=False, verbose_name="نام دامنه")
    username = models.CharField(max_length=50,null=False,blank=False, verbose_name="نام کاربری")
    password = models.CharField(max_length=50,null=False,blank=False, verbose_name="رمز عبور")
    port = models.IntegerField(null=False,blank=False, verbose_name="پورت")
    search_base = models.CharField(max_length=250,null=False,blank=False, verbose_name="پایه جستجو (Search Base)")

    access_level = models.ForeignKey('accounts.AccessLevel', verbose_name='سطح دسترسی', on_delete=models.CASCADE)

    created_at = jmodels.jDateField(auto_now_add=True, null=True, blank=True, verbose_name='زمان ایجاد')

    def __str__(self):
        return str(self.server_address)
    

class ActiveDirectoryUsers(models.Model):

    active_directory_server = models.ForeignKey(
        ActiveDirectory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="سرور اکتیو دایرکتوری مرجع"
    )

    username = models.CharField(max_length=250, verbose_name='نام کاربری')
    first_name = models.CharField(max_length=250, null=True, blank=True, verbose_name='نام')
    last_name = models.CharField(max_length=250, null=True, blank=True, verbose_name='نام خانوادگی')
    password = models.CharField(max_length=250, verbose_name='رمز عبور')
    email = models.EmailField(blank=True, null=True, verbose_name='ایمیل')

    access_level = models.ForeignKey('accounts.AccessLevel', verbose_name='سطح دسترسی', on_delete=models.CASCADE)
    
    created_at = jmodels.jDateField(auto_now_add=True, verbose_name='تاریخ ایجاد')
