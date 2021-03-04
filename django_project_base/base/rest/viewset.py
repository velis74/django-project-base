from django.db.models import Model
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django.conf import settings
from django.apps import apps


class ViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def __get_setting(self, key: str) -> list:
        _setting: list = getattr(settings, key, '').split('.')
        if len(_setting) != 2:
            raise ValueError('DJANGO_PROJECT_BASE_PROJECT_MODEL incorrectly configured')
        return _setting

    def _get_model(self, key: str) -> Model:
        return apps.get_model(
            self.__get_setting(key)[0],
            self.__get_setting(key)[1]
        )
