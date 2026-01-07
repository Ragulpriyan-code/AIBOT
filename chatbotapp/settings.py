import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url   # 👈 CORRECT IMPORT

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local env in development only
load_dotenv(BASE_DIR / ".env")

"""
Django settings for chatbotapp project.
Generated using Django 5.2.9
"""

# SECURITY
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-default-key"
)

DEBUG = True


ALLOWED_HOSTS = [
    ".onrender.com",
    "localhost",
    "127.0.0.1"
]


# APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # YOUR CHATBOT APP — KEEP LOGIC ✔
    'chatbot',
]


# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # STATIC FOR RENDER ✔
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'chatbotapp.urls'

# TEMPLATES — YOUR EXISTING UI LOGIC WORKS ✔
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'chatbotapp.wsgi.application'


# ========================================
# ❗ DATABASE — KEY FIX ✔
# ========================================

# 👉 Use Render postgres if ENV present
if os.environ.get("DATABASE_URL"):
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get("DATABASE_URL")
        )
    }
else:
    # 👉 LOCAL FALLBACK — keep for laptop only ✔
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'chatbot_db',
            'USER': 'postgres',
            'PASSWORD': 'Ragul9345',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }


# PASSWORD VALIDATION — KEEP LOGIC ✔
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ========================================
# STATIC LOGIC — YOURS ✔
# ========================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# LOGIN / LOGOUT — YOUR INTERVIEW LOGIC ✔
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
