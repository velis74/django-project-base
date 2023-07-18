from django.apps import AppConfig

from django_project_base.settings import set_django_project_base_settings


class DjangoProjectBaseConfig(AppConfig):
    name = "django_project_base"

    verbose_name = "Django Project Base"

    def ready(self):
        set_django_project_base_settings()
        import django_project_base.base.signals  # noqa: F401
