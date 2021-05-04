from django.apps import AppConfig
from django_project_base.notifications import NOTIFICATIONS_APP_ID
from django_project_base.notifications.settings import NOTIFICATIONS_SETTINGS


class DjangoProjectBaseNotifyConfig(AppConfig):
    name = NOTIFICATIONS_APP_ID
    verbose_name = "Django Project Base Notifications"

    def ready(self):
        from django.conf import settings
        for _setting in NOTIFICATIONS_SETTINGS:
            setattr(settings, _setting["name"], getattr(_setting, _setting["name"], _setting["default"]))
