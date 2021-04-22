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

# Build paths inside the project like this: BASE_DIR / 'subdir'.
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
    'rest_registration',
    'django_project_base',
    'example.demo_django_base',
    'drf_spectacular',
    'social_django',
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
        'NAME': BASE_DIR / 'db.sqlite3',
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
    )
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.microsoft.MicrosoftOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.gitlab.GitLabOAuth2',
    'social_core.backends.apple.AppleIdAuth',
    'django_project_base.base.auth_backends.UsersCachingBackend',  # cache users for auth to gain performance
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_FACEBOOK_KEY = '323344492460681'  # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = 'd61f296bdffa4cff01f3e48092a51805'  # App Secret
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_link']  # add this
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {  # add this
    'fields': 'id, name, email, picture.type(large), link'
}
SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [  # add this
    ('name', 'name'),
    ('email', 'email'),
    ('picture', 'picture'),
    ('link', 'profile_url'),
]

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '510787478378-afi3ga5m6rj23c9h2sm47563prkk3kd4.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'b0tXbSnBrRL1UvoXpqQLCY3d'

SOCIAL_AUTH_TWITTER_KEY = 'sRjQ9TBGViJ7P9QpkGlkRTTGN'
SOCIAL_AUTH_TWITTER_SECRET = 'bJKyeeniqMeHTw9ZvTbmCcyLphjTo8y8TFpwWKCHpGTlbcdVJz'
SOCIAL_AUTH_TWITTER_EXTRA_DATA = [  # add this
    ('email', 'email'),
]

SOCIAL_AUTH_MICROSOFT_GRAPH_KEY = 'c3609cf2-8999-4abd-8f76-90d20c6069ee'
SOCIAL_AUTH_MICROSOFT_GRAPH_SECRET = '4pkq_9.~EKFGI~N3S1r8ZF78aSV._Vq9_T'
SOCIAL_AUTH_MICROSOFT_GRAPH_REDIRECT_URL = 'http://localhost:8080/oauth/complete/microsoft-graph/'

SOCIAL_AUTH_GITHUB_KEY = '523b13a70d8ece2a64eb'
SOCIAL_AUTH_GITHUB_SECRET = '0945595ac7fcfb13ab0039dcc35d21e4cfb62438'

SOCIAL_AUTH_GITLAB_KEY = '8c55f7a7912587ce828ad7cf1ed83590aa5671f056f59b0220335939c3a8b1fa'
SOCIAL_AUTH_GITLAB_SECRET = '016756b4f2d9c8fe7d7032bc14c8f34c351d05fca27fe06ad642dc5bd77630c9'

SOCIAL_AUTH_APPLE_ID_CLIENT = '...'             # Your client_id com.application.your, aka "Service ID"
SOCIAL_AUTH_APPLE_ID_TEAM = '...'               # Your Team ID, ie K2232113
SOCIAL_AUTH_APPLE_ID_KEY = '...'                # Your Key ID, ie Y2P99J3N81K
SOCIAL_AUTH_APPLE_ID_SECRET = """
-----BEGIN PRIVATE KEY-----
MIGTAgE.....
-----END PRIVATE KEY-----"""
SOCIAL_AUTH_APPLE_ID_SCOPE = ['email', 'name']

SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    # 'social_core.tests.pipeline.ask_for_password',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    # 'social_core.tests.pipeline.set_password',
    'social_core.pipeline.user.user_details',
)
