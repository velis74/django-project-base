from django.db.models import Model
from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from django_project_base.base.rest.project_base_serializer import ProjectBaseSerializer
from django_project_base.base.rest.project_base_viewset import ProjectBaseViewSet
from django.apps import apps

from django_project_base.rest.project import ProjectSerializer


class ProfileSerializer(ProjectBaseSerializer):
    class Meta:
        model = None
        exclude = ()


class ProfileViewSet(ProjectBaseViewSet):
    def get_queryset(self):
        return apps.get_model(
            self._get_application_name('DJANGO_PROJECT_BASE_PROFILE_MODEL'),
            self._get_model('DJANGO_PROJECT_BASE_PROFILE_MODEL')
        ).objects.all()

    def get_serializer_class(self):
        ProfileSerializer.Meta.model = apps.get_model(
            self._get_application_name('DJANGO_PROJECT_BASE_PROFILE_MODEL'),
            self._get_model('DJANGO_PROJECT_BASE_PROFILE_MODEL'))
        return ProfileSerializer

    @action(methods=['GET'], detail=False, url_path='current', url_name='profile-current')
    def get_current_profile(self, request: Request, **kwargs) -> Response:
        user: Model = getattr(request, 'user', None)
        if not user:
            raise exceptions.AuthenticationFailed
        serializer = self.get_serializer(user.userprofile)
        response_data: dict = serializer.data
        if getattr(request, 'GET', None) and request.GET.get('decorate', '') == 'default-project':
            project_model: Model = apps.get_model(
                self._get_application_name('DJANGO_PROJECT_BASE_PROFILE_MODEL'),
                self._get_model('DJANGO_PROJECT_BASE_PROJECT_MODEL'))
            response_data['default-project'] = None
            if project_model:
                ProjectSerializer.Meta.model = project_model
                response_data['default-project'] = ProjectSerializer(
                    project_model.objects.filter(owner=user).first()).data
        return Response(response_data)
