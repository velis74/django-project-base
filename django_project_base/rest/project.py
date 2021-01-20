from django.apps import apps
from django.db.models import Model
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

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

    @action(methods=['GET'], detail=False, url_path='slug/(?P<slug>[a-zA-Z,-]+)', url_name='project-slug')
    def get_project_by_slug(self, request: Request, slug: str, **kwargs) -> Response:
        instance: Model = self.get_queryset().filter(slug=slug).first()
        if not instance:
            raise NotFound(detail='Project with project slug %s not found' % slug)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
