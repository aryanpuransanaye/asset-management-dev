from django.apps import AppConfig

class IpManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ip_management'

    def ready(self):
        # وقتی اپ آماده شد، این خط باعث می‌شود تسک‌ها در Celery ثبت شوند
        import ip_management.scanning