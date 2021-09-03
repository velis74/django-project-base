from django.apps import AppConfig

from django_project_base.notifications import NOTIFICATIONS_APP_ID
from django_project_base.notifications.settings import NOTIFICATIONS_SETTINGS
from django_project_base.settings_parser import parse_settings


class DjangoProjectBaseNotifyConfig(AppConfig):
    name = NOTIFICATIONS_APP_ID
    verbose_name = "Django Project Base Notifications"

    def ready(self):
        parse_settings(NOTIFICATIONS_SETTINGS)
