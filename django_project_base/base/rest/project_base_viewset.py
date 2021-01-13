from django.db.models import Model
from rest_framework.viewsets import ModelViewSet
from django.conf import settings


class ProjectBaseViewSet(ModelViewSet):
    def _get_setting(self, key: str) -> list:
        _setting: list = getattr(settings, key, '').split('.')
        if len(_setting) != 2:
            raise ValueError('DJANGO_PROJECT_BASE_PROJECT_MODEL incorrectly configured')
        return _setting

    def _get_model(self, key: str) -> Model:
        return self._get_setting(key)[1]

    def _get_application_name(self, key: str):
        return self._get_setting(key)[0]
