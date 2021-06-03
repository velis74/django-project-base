import swapper
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db.models import CharField, Model, Q
from django.db.models.functions import Cast
from django_project_base.rest.project import ProjectSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from dynamicforms.serializers import ModelSerializer
from dynamicforms.viewsets import ModelViewSet
from rest_framework import exceptions, filters, serializers
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


class ProfileSerializer(ModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name', read_only=True)

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        if not self._context.get('request').user.is_superuser:
            self.fields.pop('is_staff', None)
            self.fields.pop('is_superuser', None)

    def get_full_name(self, obj):
        if obj.reverse_full_name_order is None:
            reversed_order = getattr(settings, 'PROFILE_REVERSE_FULL_NAME_ORDER', False)
        else:
            reversed_order = obj.reverse_full_name_order

        if reversed_order:
            full_name = obj.last_name + ' ' + obj.first_name
        else:
            full_name = obj.first_name + ' ' + obj.last_name
        return full_name if full_name != ' ' else ''

    class Meta:
        model = swapper.load_model('django_project_base', 'Profile')
        exclude = ()


@extend_schema_view(
    destroy=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
)
class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_queryset(self):
        return swapper.load_model('django_project_base', 'Profile').objects.all()

    def get_serializer_class(self):
        return ProfileSerializer

    @action(methods=['GET'], detail=False, url_path='current', url_name='profile-current')
    def get_current_profile(self, request: Request, **kwargs) -> Response:
        user: Model = getattr(request, 'user', None)
        if isinstance(user, AnonymousUser) or not user:
            raise exceptions.AuthenticationFailed
        serializer = self.get_serializer(
            getattr(user, swapper.load_model('django_project_base', 'Profile')._meta.model_name))
        response_data: dict = serializer.data
        if getattr(request, 'GET', None) and request.GET.get('decorate', '') == 'default-project':
            project_model: Model = swapper.load_model('django_project_base', 'Project')
            response_data['default-project'] = None
            if project_model:
                ProjectSerializer.Meta.model = project_model
                response_data['default-project'] = ProjectSerializer(
                    project_model.objects.filter(owner=user).first()).data
        return Response(response_data)

    @action(methods=['GET'], detail=False, url_path=r'(?P<query>\w+)', url_name='users-search')
    def users_search(self, request: Request, query: str, **kwargs) -> Response:
        user: Model = getattr(request, 'user', None)
        if not user:
            raise exceptions.AuthenticationFailed
        profile_model: Model = swapper.load_model('django_project_base', 'Profile')
        fields: list = [f for f in profile_model._meta.fields if not f.is_relation]
        annotations: dict = {"as_str_%s" % v.name: Cast(v.name, CharField()) for v in fields}
        queries: list = [Q(**{"as_str_%s__icontains" % f.name: query}) for f in fields]
        qs = Q()
        for _query in queries:
            qs = qs | _query
        res = profile_model.objects.annotate(**annotations).filter(qs)
        return Response(self.get_serializer(res, many=True).data)
