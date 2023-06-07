from typing import List

from django.core.cache import cache
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from dynamicforms.action import Actions, TableAction, TablePosition
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.fields import IntegerField, ListField
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from django_project_base.account.constants import MERGE_USERS_QS_CK
from django_project_base.account.rest.profile import ProfileSerializer, ProfileViewSet
from example.demo_django_base.models import MergeUserGroup


class ProfileMergeSerializer(ProfileSerializer):
    template_context = dict(url_reverse="profile-merge-base-project")

    form_titles = {
        "table": "User Merge profiles",
        "new": "",
        "edit": "",
    }

    actions = Actions(add_form_buttons=False)

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        self.actions.actions = (
            TableAction(
                TablePosition.ROW_END,
                label=_("Remove"),
                title=_("Remove"),
                name="delete",
                icon="person-remove-outline",
            ),
            TableAction(
                TablePosition.HEADER,
                label=_("Merge"),
                title=_("Merge"),
                name="merge-users",
                icon="git-merge-outline",
            ),
            TableAction(
                TablePosition.HEADER,
                label=_("Clear all"),
                title=_("Clear all"),
                name="clear-merge-users",
                icon="remove-circle-outline",
            ),
        )

    @property
    def filter_data(self):
        return None

    class Meta(ProfileSerializer.Meta):
        pass


class MergeUsersRequest(Serializer):
    users = ListField(child=IntegerField(min_value=1), required=True, allow_empty=False)

    def validate(self, attrs):
        for user in attrs["users"]:
            if MergeUserGroup.objects.filter(users__icontains=user).exists():
                raise ValidationError(dict(users=f"Pk {user} is present in another group"))
        return super().validate(attrs)


@extend_schema_view(
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
)
class ProfileMergeViewSet(ProfileViewSet):
    serializer_class = ProfileMergeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self) -> List:
        ck_val = cache.get(MERGE_USERS_QS_CK % self.request.user.pk, [])
        if not ck_val:
            return super().get_queryset().filter(pk=-1)
        return super().get_queryset().filter(pk__in=ck_val)

    def get_serializer_class(self):
        return ProfileMergeSerializer

    # TODO: REMOVE THIS
    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        request._dont_enforce_csrf_checks = True
        return request

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "search", description="Search users by all of those fields: username, email, first_name, last_name"
            )
        ],
        description="Get list of users",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK", response=ProfileMergeSerializer),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(exclude=True)
    @transaction.atomic
    def create(self, request: Request, *args, **kwargs) -> Response:
        ck = MERGE_USERS_QS_CK % self.request.user.pk
        ser = MergeUsersRequest(data=dict(users=cache.get(ck, [])))
        ser.is_valid(raise_exception=True)
        group, created = MergeUserGroup.objects.get_or_create(
            users=",".join(map(str, ser.validated_data["users"])), created_by=self.request.user.pk
        )
        cache.set(ck, [])
        return Response({MergeUserGroup._meta.pk.name: group.pk})

    @extend_schema(exclude=True)
    def retrieve(self, request, *args, **kwargs):
        raise super().retrieve(request, args, kwargs)

    @extend_schema(exclude=True)
    def get_current_profile(self, request: Request, **kwargs) -> Response:
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)

    @extend_schema(exclude=True)
    def mark_current_profile_delete(self, request: Request, **kwargs) -> Response:
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        pk = self.get_object().pk
        ck = MERGE_USERS_QS_CK % self.request.user.pk
        ck_val = cache.get(ck, [])
        ck_val = [i for i in ck_val if i != pk]
        cache.set(ck, list(set(ck_val)), timeout=None)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)

    @extend_schema(
        description="Clear users to be merged",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="OK"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    @action(
        methods=["DELETE"],
        detail=False,
        url_path="clear",
        url_name="clear",
        permission_classes=[IsAuthenticated, IsAdminUser],
    )
    def clear(self, request: Request, **kwargs) -> Response:
        cache.set(MERGE_USERS_QS_CK % self.request.user.pk, [])
        MergeUserGroup.objects.filter(created_by=self.request.user.pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
