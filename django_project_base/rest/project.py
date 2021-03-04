from typing import Union

from django.apps import apps
from django.conf import settings
from django.http import Http404

from django_project_base.base.rest.project_base_serializer import ProjectBaseSerializer
from django_project_base.base.rest.project_base_viewset import ProjectBaseViewSet


class ProjectSerializer(ProjectBaseSerializer):
    class Meta:
        model = None
        exclude = ()


class ProjectViewSet(ProjectBaseViewSet):

    def get_queryset(self):
        return apps.get_model(
            self._get_application_name('DJANGO_PROJECT_BASE_PROJECT_MODEL'),
            self._get_model('DJANGO_PROJECT_BASE_PROJECT_MODEL')
        ).objects.all()

    def get_serializer_class(self):
        ProjectSerializer.Meta.model = apps.get_model(
            self._get_application_name('DJANGO_PROJECT_BASE_PROJECT_MODEL'),
            self._get_model('DJANGO_PROJECT_BASE_PROJECT_MODEL'))
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
