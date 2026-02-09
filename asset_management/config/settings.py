import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-m_&aa@wgk+0)he=9(p$39p@@cgj$wq1$_ea+dkh8kdk1c&qz&@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*'] # برای لوکال هاست همه را باز می‌گذاریم

AUTH_USER_MODEL = 'accounts.User'

# 2FA LOGIN
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'aryanpuransanayeh@gmail.com'
EMAIL_HOST_PASSWORD = 'ikgd macw aawp lqir'

# Celery
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Whitenoise
    'whitenoise.runserver_nostatic', 
    
    'core',
    'accounts',
    'ip_management',
    'data_and_information',
    'software',
    'services',
    'hardware',
    'places_and_areas',
    'human_resources',
    'infrastructure_assets',
    'intangible_assets',
    'supplier',
    'ticket',
    'organization',
    'active_directory',
    
    'mptt',
    'django_jalali',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

SIMPLE_JWT = {
    'BLACKLIST_AFTER_ROTATION': False,
    'ACCESS_TOKEN_LIFETIME': timedelta(days=365 * 50),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=365 * 60),
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    
    # Whitenoise باید بعد از SecurityMiddleware باشد
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # مسیر پوشه‌ای که فایل index.html در آن است
        'DIRS': [BASE_DIR / 'frontend_dist'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- تنظیمات Static Files (بسیار مهم) ---

# تغییر مهم: چون Nuxt فایل‌ها را با مسیر /_nuxt/ لود می‌کند،
# ما STATIC_URL را خالی می‌گذاریم تا روت اصلی را پوشش دهد.
# اما چون ممکن است با فایل‌های دیگر تداخل داشته باشد، روش بهتر این است که 
# STATIC_URL را /static/ نگه داریم و در urls.py هندل کنیم.
# اما برای اینکه Whitenoise فایل‌های داخل frontend_dist را سرو دهد، 
# باید آن را در STATICFILES_DIRS معرفی کنیم.

STATIC_URL = '/static/' 
MEDIA_URL = '/media/'

# 1. معرفی پوشه frontend_dist به عنوان منبع فایل استاتیک
STATICFILES_DIRS = [
    BASE_DIR / 'frontend_dist',
]

# 2. پوشه‌ای که collectstatic فایل‌ها را در آن کپی می‌کند (برای پروداکشن)
STATIC_ROOT = BASE_DIR / 'staticfiles' 

# تنظیمات Whitenoise برای فشرده‌سازی و مانیفست
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.validation.NumericPasswordValidator',
#     },
# ]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True