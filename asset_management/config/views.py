from django.shortcuts import render
from django.conf import settings
from pathlib import Path

def serve_frontend(request):
    """
    این ویو تمام درخواست‌هایی که به API یا فایل استاتیک مربوط نیستند
    را به فایل index.html اصلی Nuxt ارجاع می‌دهد.
    جاوااسکریپت Nuxt بقیه کارها (مثل نمایش صفحه Dashboard) را انجام می‌دهد.
    """
    # مسیر فایل index.html در پوشه frontend_dist
    frontend_path = Path(settings.BASE_DIR) / 'frontend_dist' / 'index.html'
    
    # چک می‌کنیم که فایل وجود دارد
    if not frontend_path.exists():
        raise FileNotFoundError(f"فایل {frontend_path} پیدا نشد. لطفا فایل‌های Nuxt را کپی کنید.")

    return render(request, str(frontend_path))