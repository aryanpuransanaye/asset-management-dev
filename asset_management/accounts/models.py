from django.db import models
from django.contrib.auth.models import AbstractUser
from django_jalali.db import models as jmodels
from mptt.models import MPTTModel, TreeForeignKey
from active_directory.models import ActiveDirectory


class AccessLevel(MPTTModel):
    level_name = models.CharField(max_length=50, verbose_name='نام سطح')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='سطح بالادستی')
    main_level = models.BooleanField(default=False, verbose_name='سطح اصلی است؟')
    class MPTTMeta:
        order_insertion_by = ['level_name']

    def __str__(self):
        return str(self.level_name)
    
    @property
    def main_level_name(self):
        root = self.get_root()
        return root.level_name if root else self.level_name


class User(AbstractUser):
    
    """
    Custom User model extending Django's AbstractUser.
    Additional fields can be added here as needed.
    """

    GENDER_CHOICES = (
        ('male', 'مرد'),
        ('female', 'زن'),
        ('other', 'سایر'),
    ) 


    username = models.CharField(max_length=255, verbose_name='نام کاربری', unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام')
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='نام خانوادگی')

    access_level = models.ForeignKey(AccessLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name="users", verbose_name='سطح دسترسی')
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='جنسیت')
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='شماره تماس')
    email = models.EmailField(null=True, blank=True, verbose_name='ایمیل')
    address = models.TextField(blank=True, null=True, verbose_name='آدرس')
    created_at = jmodels.jDateField(auto_now_add=True, verbose_name='تاریخ ثبت‌نام')
    updated_at = jmodels.jDateField(auto_now=True, verbose_name='آخرین ویرایش پروفایل')
    last_login = jmodels.jDateField(blank=True, null=True, verbose_name='آخرین ورود')
    ip_login = models.GenericIPAddressField(blank=True, null=True, verbose_name='آخرین IP ورود')

    # 2FA Temp fields
    otp_code = models.CharField(max_length=6, blank=True, null=True, verbose_name='کد تایید (OTP)')
    otp_created_at = models.DateTimeField(blank=True, null=True, verbose_name='زمان ایجاد کد تایید')

    #change password
    requirement_to_change_the_password = models.BooleanField(default=False, verbose_name="اجبار برای تغییر رمز عبور")


    #for Active Direcory's users
    active_directory_server = models.ForeignKey(
        ActiveDirectory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="سرور اکتیو دایرکتوری مرجع"
    )

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='custom_user_set',  # Changed related_name to avoid clashes
        related_query_name='user',
        verbose_name='گروه‌ها'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # Changed related_name to avoid clashes
        related_query_name='user',
        verbose_name='مجوزهای کاربر'
    )

    def __str__(self):
        return self.username
    

class SystemAccessPermission(models.Model):
    class Meta:
        managed = False
        default_permissions = ()

        permissions = [
            ('asset_ip_manage_crud', 'مدیریت کامل رکوردهای IP (ایجاد، مشاهده، ویرایش، حذف)'),
            ('asset_ip_manage_r', 'فقط مشاهده رکوردهای IP'),

            ('asset_data_and_information_crud', 'مدیریت کامل داده‌ها و اطلاعات'),
            ('asset_data_and_information_r', 'فقط مشاهده داده‌ها و اطلاعات'),

            ('asset_software_crud', 'مدیریت کامل نرم‌افزارها'),
            ('asset_software_r', 'فقط مشاهده نرم‌افزارها'),

            ('asset_services_crud', 'مدیریت کامل سرویس‌ها'),
            ('asset_services_r', 'فقط مشاهده سرویس‌ها'),

            ('asset_hardware_crud', 'مدیریت کامل سخت‌افزارها'),
            ('asset_hardware_r', 'فقط مشاهده سخت‌افزارها'),

            ('asset_place_and_areas_crud', 'مدیریت کامل اماکن و محوطه‌ها'),
            ('asset_place_and_areas_r', 'فقط مشاهده اماکن و محوطه‌ها'),

            ('asset_human_resources_crud', 'مدیریت کامل منابع انسانی'),
            ('asset_human_resources_r', 'فقط مشاهده منابع انسانی'),

            ('asset_infrastructure_assets_crud', 'مدیریت کامل زیرساخت‌ها'),
            ('asset_infrastructure_assets_r', 'فقط مشاهده زیرساخت‌ها'),

            ('asset_intangible_assets_crud', 'مدیریت کامل دارایی‌های نامشهود'),
            ('asset_intangible_assets_r', 'فقط مشاهده دارایی‌های نامشهود'),

            ('asset_suppliers_crud', 'مدیریت کامل تامین‌کنندگان'),
            ('asset_suppliers_r', 'فقط مشاهده تامین‌کنندگان'),
            
            ('can_use_scanners', 'امکان استفاده از اسکنرهای دارایی'),

            ('ticket_can_response_to_tickets', 'امکان پاسخگویی به تیکت‌ها'),
            ('ticket_can_manage_helpdesk_setting', 'مدیریت تنظیمات هلپ‌دسک'),
            ('ticket_can_answer_questions', 'امکان پاسخ به سوالات کاربران'),
        ]


class Active_directory_model(models.Model):

    server_address = models.CharField(max_length=50, verbose_name='آدرس سرور (IP/Domain)')
    domain_name = models.CharField(max_length=50, verbose_name='نام دامنه (Domain Name)')
    username = models.CharField(max_length=50, verbose_name='نام کاربری اتصال')
    password = models.CharField(max_length=50, verbose_name='رمز عبور اتصال')
    port = models.IntegerField(verbose_name='پورت اتصال')
    search_base = models.CharField(max_length=50, verbose_name='پایه جستجو (Search Base)')

    def __str__(self):
        return f"{self.domain_name} ({self.server_address})"