from django.db.models import CharField, Model, Q
from django.db.models.functions import Cast
from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from django_project_base.base.rest.serializer import Serializer as ProjectBaseSerializer
from django_project_base.base.rest.viewset import ViewSet as ProjectBaseViewSet
from django_project_base.rest.project import ProjectSerializer


class ProfileSerializer(ProjectBaseSerializer):
    class Meta:
        model = None
        exclude = ()


class ProfileViewSet(ProjectBaseViewSet):
    def get_queryset(self):
        return self._get_model('DJANGO_PROJECT_BASE_PROFILE_MODEL').objects.all()

    def get_serializer_class(self):
        ProfileSerializer.Meta.model = self._get_model('DJANGO_PROJECT_BASE_PROFILE_MODEL')
        return ProfileSerializer

    @action(methods=['GET'], detail=False, url_path='current', url_name='profile-current')
    def get_current_profile(self, request: Request, **kwargs) -> Response:
        user: Model = getattr(request, 'user', None)
        if not user:
            raise exceptions.AuthenticationFailed
        serializer = self.get_serializer(user.userprofile)
        response_data: dict = serializer.data
        if getattr(request, 'GET', None) and request.GET.get('decorate', '') == 'default-project':
            project_model: Model = self._get_model('DJANGO_PROJECT_BASE_PROJECT_MODEL')
            response_data['default-project'] = None
            if project_model:
                ProjectSerializer.Meta.model = project_model
                response_data['default-project'] = ProjectSerializer(
                    project_model.objects.filter(owner=user).first()).data
        return Response(response_data)

    @action(methods=['GET'], detail=False, url_path=r'search/(?P<query>\w+)', url_name='users-search')
    def users_search(self, request: Request, query: str, **kwargs) -> Response:
        user: Model = getattr(request, 'user', None)
        if not user:
            raise exceptions.AuthenticationFailed
        profile_model: Model = self._get_model('DJANGO_PROJECT_BASE_PROFILE_MODEL')
        fields: list = [f for f in profile_model._meta.fields if not f.is_relation]
        annotations: dict = {"as_str_%s" % v.name: Cast(v.name, CharField()) for v in fields}
        queries: list = [Q(**{"as_str_%s__icontains" % f.name: query}) for f in fields]
        qs = Q()
        for _query in queries:
            qs = qs | _query
        res = profile_model.objects.annotate(**annotations).filter(qs)
        return Response(self.get_serializer(res, many=True).data)
