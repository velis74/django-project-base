from enum import IntEnum
from typing import Dict, Union

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from dynamicforms.serializers import Serializer
from rest_framework.utils.model_meta import get_field_info


def set_django_security(django_settings, deploy=True, swagger_version=None):
    """
    Sets django web security settings.
    Call this from settings.py

    :param django_settings: globals() of your application
    :param deploy: True if server is deployed, False for development
    :param swagger_version: If you are using swagger or drf_spectacular set swagger version to allow CSP to access
        swagger files.
    :return:
    """

    for app in ["django_permissions_policy", "csp"]:
        if app not in django_settings["INSTALLED_APPS"]:
            django_settings["INSTALLED_APPS"].append(app)

    for middleware in ["django_permissions_policy.PermissionsPolicyMiddleware", "csp.middleware.CSPMiddleware"]:
        if middleware not in django_settings["MIDDLEWARE"]:
            django_settings["MIDDLEWARE"].append(middleware)

    django_settings["SECURE_BROWSER_XSS_FILTER"] = True
    django_settings["SECURE_CONTENT_TYPE_NOSNIFF"] = True

    if deploy:
        django_settings["SECURE_SSL_REDIRECT"] = True
        django_settings["SECURE_PROXY_SSL_HEADER"] = ("HTTP_X_FORWARDED_PROTO", "https")

        django_settings["CSRF_COOKIE_SECURE"] = True
        django_settings["CSRF_COOKIE_NAME"] = "__Host-csrftoken"
        django_settings["SESSION_COOKIE_SECURE"] = True
        django_settings["SESSION_COOKIE_NAME"] = "__Host-sessionid"

        django_settings["SECURE_HSTS_SECONDS"] = 15768000  # 6 Months
        django_settings["SECURE_HSTS_INCLUDE_SUBDOMAINS"] = True
        django_settings["SECURE_HSTS_PRELOAD"] = True

    django_settings["CSRF_COOKIE_HTTPONLY"] = True
    django_settings["SESSION_COOKIE_HTTPONLY"] = True

    django_settings["CSRF_COOKIE_SAMESITE"] = "Strict"
    django_settings["SESSION_COOKIE_SAMESITE"] = "Strict"

    # CSP can be changed per request... with decorator:
    #  https://django-csp.readthedocs.io/en/latest/decorators.html#decorator-chapter
    # Content Security Policy
    django_settings["CSP_DEFAULT_SRC"] = [
        "'none'",
    ]
    # stackpath.bootstrapcdn.com - because of (old) login
    django_settings["CSP_STYLE_SRC"] = [
        "'self'",
        "'unsafe-inline'",
        "cdnjs.cloudflare.com",
        "stackpath.bootstrapcdn.com",
    ]
    # unsafe-eval - because of Vue.js
    # code.jquery.com, stackpath.bootstrapcdn.com, connect.facebook.net - because of (old) login
    django_settings["CSP_SCRIPT_SRC"] = [
        "'self'",
        "'unsafe-inline'",
        "'unsafe-eval'",
        "code.jquery.com",
        "stackpath.bootstrapcdn.com",
        "connect.facebook.net",
    ]
    # via.placeholder.com - because of default user logo
    django_settings["CSP_IMG_SRC"] = ["'self'", "via.placeholder.com"]

    if swagger_version:
        django_settings["CSP_STYLE_SRC"].append("unpkg.com/swagger-ui-dist@%s/" % swagger_version)
        django_settings["CSP_SCRIPT_SRC"].append("unpkg.com/swagger-ui-dist@%s/" % swagger_version)
        django_settings["CSP_IMG_SRC"].append("unpkg.com/swagger-ui-dist@%s/" % swagger_version)

    django_settings["CSP_FONT_SRC"] = ["'self'", "cdnjs.cloudflare.com"]
    django_settings["CSP_CONNECT_SRC"] = [
        "'self'",
    ]
    django_settings["CSP_OBJECT_SRC"] = [
        "'none'",
    ]
    django_settings["CSP_BASE_URI"] = [
        "'self'",
    ]
    django_settings["CSP_FRAME_ANCESTORS"] = [
        "'none'",
    ]
    django_settings["CSP_FORM_ACTION"] = [
        "'self'",
    ]

    django_settings["PERMISSIONS_POLICY"] = {
        "accelerometer": [],
        "ambient-light-sensor": [],
        "autoplay": [],
        # "battery": [],
        "camera": [],
        "display-capture": [],
        "document-domain": [],
        "encrypted-media": [],
        "fullscreen": [],
        "gamepad": [],
        "geolocation": [],
        "gyroscope": [],
        "interest-cohort": [],
        "magnetometer": [],
        "microphone": [],
        "midi": [],
        "payment": [],
        "picture-in-picture": [],
        "publickey-credentials-get": [],
        "screen-wake-lock": [],
        # "speaker-selection": [],
        "sync-xhr": [],
        "usb": [],
        "web-share": [],
        "xr-spatial-tracking": [],
    }


class IntDescribedEnum(IntEnum):
    def __new__(cls, *args, **kwds):
        obj = int.__new__(cls, args[0])
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by new
    def __init__(self, _: str, description: str = None, data: dict = None):
        self._description_ = description
        self._data_ = data

    description = property(lambda self: self._description_)
    data = property(lambda self: self._data_)

    @classmethod
    def get_choices_tuple(cls):
        return tuple((item, item.description) for item in cls)

    @classmethod
    def has_value(cls, value):
        return value in cls.__members__.values()


def get_pk_name(obj: Union[Model, QuerySet, Dict, Serializer], model: Model = None):
    if isinstance(obj, QuerySet):
        return obj.model._meta.pk.name
    if isinstance(obj, Model):
        return obj._meta.pk.name
    return get_field_info(model if model else obj).pk.name


def get_host_url(request: HttpRequest) -> str:
    host_url = "%s://%s" % ("https" if request.is_secure() else "http", request.META["HTTP_HOST"])
    if not host_url.endswith("/"):
        host_url += "/"
    return host_url
