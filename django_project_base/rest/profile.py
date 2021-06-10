import datetime

import swapper
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db.models import Model
from django.utils import timezone
from django_project_base.rest.project import ProjectSerializer
from django_project_base.settings import DELETE_PROFILE_TIMEDELTA, DJANGO_USER_CACHE
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from dynamicforms.serializers import ModelSerializer
from dynamicforms.viewsets import ModelViewSet
from rest_framework import exceptions, filters, serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response


class ProfileSerializer(ModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name', read_only=True)
    delete_at = serializers.DateTimeField(write_only=True)

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
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
)
class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_queryset(self):
        return swapper.load_model('django_project_base', 'Profile').objects.all()

    def get_serializer_class(self):
        return ProfileSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdminUser(), ]
        return super(ProfileViewSet, self).get_permissions()

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
        description="Get user profile of calling user.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK'),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Not allowed')
        }
    )
    @action(methods=['GET'], detail=False, url_path='current', url_name='profile-current',
            permission_classes=[IsAuthenticated])
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

    @extend_schema(
        description="Marks profile of calling user for deletion in future. Future date is determined "
                    "by settings",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description='No content'),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Not allowed')
        }
    )
    @get_current_profile.mapping.delete
    def mark_current_profile_delete(self, request: Request, **kwargs) -> Response:
        user: Model = getattr(request, 'user', None)
        if not user:
            raise exceptions.AuthenticationFailed
        user.is_active = False
        profile_obj = getattr(user, swapper.load_model('django_project_base', 'Profile')._meta.model_name)
        profile_obj.delete_at = timezone.now() + datetime.timedelta(days=DELETE_PROFILE_TIMEDELTA)

        profile_obj.save()
        user.save()
        cache.delete(DJANGO_USER_CACHE % user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description="Immediately removes user from database",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="No content"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super(ProfileViewSet, self).destroy(request, *args, **kwargs)
