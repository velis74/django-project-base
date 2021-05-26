"""
Django settings for demo_app project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path

from django_project_base import VERSION
# Build paths inside the project like this: BASE_DIR / 'subdir'.
from django_project_base.notifications import NOTIFICATIONS_APP_ID
from django_project_base.accounts import ACCOUNT_APP_ID

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w0o6y0rwef0zijgd7m91w0b!p-(#l1zpna1%c1vvr7f17)x&*-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    # 'django.contrib.sites',
    'rest_registration',
    'django_project_base',
    'example.demo_django_base',
    'drf_spectacular',
    NOTIFICATIONS_APP_ID,
    'social_django',
    ACCOUNT_APP_ID,
]

MIDDLEWARE = [
    'django_project_base.base.middleware.UrlVarsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_project_base.performance_middleware.middleware.profile_middleware.profile_middleware'
]

ROOT_URLCONF = 'example.setup.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'example.setup.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),

    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    str(BASE_DIR).replace('example', '') + 'django_project_base/locale/'
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static/'),
    str(BASE_DIR).replace('example', '') + 'django_project_base/static/'
)

DJANGO_PROJECT_BASE_PROJECT_MODEL = 'demo_django_base.Project'
DJANGO_PROJECT_BASE_PROFILE_MODEL = 'demo_django_base.UserProfile'

REST_REGISTRATION = {
    'REGISTER_VERIFICATION_ENABLED': False,
    'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
    'RESET_PASSWORD_VERIFICATION_ENABLED': False,
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'dynamicforms.renderers.TemplateHTMLRenderer',
    )
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Project Base Example API',
    'DESCRIPTION': 'Django project base',
    'VERSION': VERSION,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'defaultModelsExpandDepth': -1,
    },
    'COMPONENT_SPLIT_REQUEST': True,
}

AUTHENTICATION_BACKENDS = (
    'django_project_base.base.auth_backends.UsersCachingBackend',  # cache users for auth to gain performance
    'django.contrib.auth.backends.ModelBackend',
)

WSGI_LOG_LONG_REQUESTS = True

from sett_tmp import *

