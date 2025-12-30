from django.db import models
from core.models import BaseAsset

class DataAndInformation(BaseAsset):

    LEVEL = (
        ('0', 'خصوصی'),
        ('1', 'محرمانه'),
        ('2', 'عمومی')
    )

    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام')
    location = models.CharField(max_length=255, null=True, blank=True, default='-', verbose_name='محل نگهداری')
    usage = models.CharField(max_length=255, null=True, blank=True, default='-', verbose_name= 'مورد مصرف')
    owner = models.CharField(max_length=255, null=True, blank=True, default='-', verbose_name='مالک')
    confidentiality_level = models.CharField(max_length=400, choices=LEVEL, null=True, blank=True, default='-', verbose_name='سطح محرمانگی')
    version = models.CharField(max_length=255, null=True, blank=True, default='-', verbose_name='نسخه')
    document_type = models.CharField(max_length=255, null=True, blank=True, default='-', verbose_name='نوع مسنتد')

    def __str__(self):
        return str(self.id)

