from django.db import models
from django_jalali.db import models as jmodels
from accounts.models import User, AccessLevel

class Question(models.Model):

    text = models.CharField(max_length=255, unique=True, verbose_name="متن سوال")
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', verbose_name="کاربر")

    def __str__(self):
        return self.text


class MessageCategory(models.Model):
    
    text = models.CharField(max_length=100, unique=True, verbose_name="عنوان دسته بندی")
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_category', verbose_name="کاربر")

    def __str__(self):
        return self.text


class TicketRoom(models.Model):

    PRIORITY_CHOICES = (
        ('0', 'کم اهمیت'),
        ('1', 'معمولی'),
        ('2', 'ویژه'),
    )

    ASSET_CATEGORIES = (
        ('0', 'بدون دسته‌بندی'),
        ('1', 'داده‌ها و اطلاعات'),
        ('2', 'نرم‌افزار'),
        ('3', 'سرویس'),
        ('4', 'سخت‌افزار'),
        ('5', 'اماکن و محوطه'),
        ('6', 'منابع انسانی'),
        ('7', 'دارایی‌های زیرساختی'),
        ('8', 'دارایی‌های نامشهود'),
        ('9', 'تامین‌کنندگان'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets', verbose_name="کاربر")
    user_info_summary = models.CharField(max_length=255, verbose_name="اطلاعات کاربر (IP یا نام)")
    
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="موضوع سوال")
    
    is_active = models.BooleanField(default=True, verbose_name="اتاق فعال است؟")
    requires_password_reset = models.BooleanField(default=False, verbose_name="درخواست رمز عبور")
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    
    additional_details = models.TextField(blank=True, null=True, verbose_name="توضیحات تکمیلی")
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=1, default='1', verbose_name="اولویت")
    access_level = models.ForeignKey(AccessLevel, on_delete=models.PROTECT, blank=True, null=True, verbose_name="سطح دسترسی")

    category = models.ForeignKey(MessageCategory, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="دسته بندی پیام")
    related_asset_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="آیدی دارایی مرتبط")
    related_asset_category = models.CharField(choices=ASSET_CATEGORIES, max_length=2, blank=True, null=True, verbose_name="گروه دارایی مرتبط")


    def __str__(self):
        return f"{self.user_info_summary} - {self.created_at}"


class TicketMessage(models.Model):

    ticket_room = models.ForeignKey(TicketRoom, on_delete=models.CASCADE, related_name='messages', verbose_name="اتاق تیکت")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="فرستنده")
    content = models.TextField(verbose_name="متن پیام")
    
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    read_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='read_messages', verbose_name="خوانده شده توسط")
    
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name="زمان ارسال")
    seen_at = jmodels.jDateTimeField(null=True, blank=True, verbose_name="زمان مشاهده")


    def __str__(self):
        return f"Message from {self.sender} in {self.ticket_room}"