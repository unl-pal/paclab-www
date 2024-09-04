"""
Django settings for paclab project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from glob import glob
from decouple import config, Csv
import dj_database_url
import logging.config
from django.utils.log import DEFAULT_LOGGING

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)
MAINTENANCE_MODE = config('MAINTENANCE_MODE', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
ADMINS = ((config('ADMIN_NAME', default='PAClab Admin'), config('ADMIN_EMAIL', default='')), )

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'widget_tweaks',
    'django_countries',
]

# Set this setting to true in your env file if you would like to use the hijack app
USE_HIJACK = config('USE_HIJACK', default=False, cast=bool)

HIJACK_ALLOW_GET_REQUESTS = True # enable Hijack admin page
HIJACK_USE_BOOTSTRAP = True

if USE_HIJACK == True:
    INSTALLED_APPS += [
        'hijack',
        'compat',
        'hijack_admin',
    ]

if DEBUG == True:
    INSTALLED_APPS += [
        'django_extensions',
    ]

INSTALLED_APPS += [
    'website.apps.WebsiteConfig',
    'backend.apps.BackendConfig',
]

LOGGING_CONFIG = None
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'formatters': {
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true', ],
            'class': 'logging.StreamHandler',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', ],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'error_file': {
            'level': 'ERROR',
            'filters': ['require_debug_false', ],
            'class': 'logging.FileHandler',
            'filename': config('ERROR_LOG', default='/home/boa/paclab/error.log'),
        },
    },
    'loggers': {
        'django': {
            'level': 'DEBUG',
            'handlers': ['console', 'mail_admins', 'error_file', ],
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console', ],
            'propagate': False,
        },
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    }
})

# SSL-only websites can increase security settings
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)

X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'website.middleware.SiteMaintenanceMiddleware',
]

ROOT_URLCONF = 'paclab.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'website.context_processors.adminConstant',
                'website.context_processors.moderatorConstant',
                'website.context_processors.retiredConstant',
                'website.context_processors.useHijack',
                'website.context_processors.in_maintenance',
            ],
        },
    },
]

WSGI_APPLICATION = 'paclab.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

FIXTURE_DIRS = glob(os.path.join(BASE_DIR, '*_backend/fixtures'))

REPO_PATH = config('REPO_PATH', default='.')
TRANSFORMED_PATH = config('TRANSFORMED_PATH', default='.')

MAX_FILE_UPLOAD = 8 * 1024 * 1024
THUMBNAIL_SIZE = (200, 200)

if DEBUG == True:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_USER')
    EMAIL_HOST_PASSWORD = config('EMAIL_PASSWORD')

SEND_BROKEN_LINK_EMAILS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Login Required Redirect URLs
LOGIN_REDIRECT_URL = config('LOGIN_REDIRECT_URL', default='website:index')
LOGIN_URL = config('LOGIN_URL', default='website:login')

# configure messages for Bootstrap
from django.contrib import messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}
