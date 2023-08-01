from django.apps import AppConfig


class DjangoProjectBaseCeleryConfig(AppConfig):
    name = "celery"
    verbose_name = "Django Project Base Celery"

    def ready(self):
        pass
