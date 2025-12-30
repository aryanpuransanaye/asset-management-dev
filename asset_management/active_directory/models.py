from django.db import models

class ActiveDirectory(models.Model) :
    server_address = models.CharField(max_length=50,null=False,blank=False, verbose_name="آدرس سرور")
    domain_name = models.CharField(max_length=50,null=False,blank=False, verbose_name="نام دامنه")
    username = models.CharField(max_length=50,null=False,blank=False, verbose_name="نام کاربری")
    password = models.CharField(max_length=50,null=False,blank=False, verbose_name="رمز عبور")
    port = models.IntegerField(null=False,blank=False, verbose_name="پورت")
    search_base = models.CharField(max_length=250,null=False,blank=False, verbose_name="پایه جستجو (Search Base)")

    def __str__(self):
        return str(self.server_address)