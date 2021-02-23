from django.apps import AppConfig

from django_project_base.settings import SETTINGS


class DjangoProjectBaseConfig(AppConfig):
    name = 'django_project_base'
    verbose_name = "Django REST framework"

    def ready(self):
        from django.conf import settings
        for _setting in SETTINGS:
            setattr(settings, _setting["name"], getattr(_setting, _setting["name"], _setting["default"]))
