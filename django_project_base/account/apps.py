from django.apps import AppConfig

from django_project_base.account import ACCOUNT_APP_ID
from django_project_base.account.settings import ACCOUNT_SETTINGS
from django_project_base.settings_parser import parse_settings


class DjangoProjectBaseAccountsConfig(AppConfig):
    name = ACCOUNT_APP_ID
    verbose_name = "Django Project Base Account management"

    def ready(self):
        parse_settings(ACCOUNT_SETTINGS)
