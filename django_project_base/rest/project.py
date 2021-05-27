from typing import Union

import swapper
from django.conf import settings
from django.http import Http404
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = swapper.load_model('django_project_base', 'Project')
        exclude = ()


class ProjectViewSet(ModelViewSet):

    def get_queryset(self):
        return swapper.load_model('django_project_base', 'Project').objects.all()

    def get_serializer_class(self):
        return ProjectSerializer

    def get_object(self):

        SLUG_FIELD_NAME: str = settings.DJANGO_PROJECT_BASE_SLUG_FIELD_NAME

        lookup_field: str = self.lookup_field
        lookup_field_val: Union[str, int] = self.kwargs.get(self.lookup_field)

        def set_args(name: str) -> None:
            self.kwargs.pop(lookup_field, None)
            self.kwargs[name] = lookup_field_val
            self.lookup_field = name

        if lookup_field == 'pk' or lookup_field == self.get_queryset().model._meta.pk.name:
            is_pk_auto_field: bool = self.get_queryset().model._meta.pk.get_internal_type() == 'AutoField'
            try:
                int(lookup_field_val) if is_pk_auto_field else None
                return super().get_object()
            except (ValueError, Http404):
                set_args(SLUG_FIELD_NAME)
                return super().get_object()
        return super().get_object()
