from django.apps import apps

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
