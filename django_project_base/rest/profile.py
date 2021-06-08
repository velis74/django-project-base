import swapper
from django.conf import settings
from django.db.models import Model
from django_project_base.rest.project import ProjectSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from dynamicforms.serializers import ModelSerializer
from dynamicforms.viewsets import ModelViewSet
from rest_framework import exceptions, filters, serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
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
            return obj.last_name + ' ' + obj.first_name
        else:
            return obj.first_name + ' ' + obj.last_name

    class Meta:
        model = None
        exclude = ()


@extend_schema_view(
    create=extend_schema(exclude=True),
    destroy=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
)
class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_queryset(self):
        return swapper.load_model('django_project_base', 'Profile').objects.all()

    def get_serializer_class(self):
        ProfileSerializer.Meta.model = swapper.load_model('django_project_base', 'Profile')
        return ProfileSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter('search',
                             description="Search users by all of those fields: username, email, first_name, last_name")
        ],
        description="Get list of users",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK', response=get_serializer_class),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Not allowed')
        }
    )
    def list(self, request, *args, **kwargs):
        return super(ProfileViewSet, self).list(request, *args, **kwargs)

    def create(self, request: Request, *args, **kwargs) -> Response:
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description='Get user profile by id',
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK', response=get_serializer_class),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Not allowed')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super(ProfileViewSet, self).retrieve(request, *args, **kwargs)

    @extend_schema(
        description='Update profile data (partially)',
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK',
                                                response=get_serializer_class),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Not allowed')
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super(ProfileViewSet, self).partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Get user profile of calling user",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK'),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Not allowed')
        }
    )
    @action(methods=['GET'], detail=False, url_path='current', url_name='profile-current')
    def get_current_profile(self, request: Request, **kwargs) -> Response:
        user: Model = getattr(request, 'user', None)
        if not user:
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
