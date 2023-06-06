from typing import List

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from dynamicforms.action import Actions, TableAction, TablePosition
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from django_project_base.account.rest.profile import ProfileSerializer, ProfileViewSet


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
                label=_("AAA"),
                title=_("AAA"),
                name="add-to-group",
                icon="alert-circle-outline",
            ),
            TableAction(
                TablePosition.HEADER,
                label=_("Merge"),
                title=_("Merge"),
                name="merge-users",
                icon="aperture-outline",
            ),
            TableAction(
                TablePosition.HEADER,
                label=_("Clear"),
                title=_("Clear"),
                name="clear-merge-users",
                icon="nuclear-outline",
            ),
        )

    @property
    def filter_data(self):
        return None

    class Meta(ProfileSerializer.Meta):
        pass


@extend_schema_view(
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
)
class ProfileMergeViewSet(ProfileViewSet):
    serializer_class = ProfileMergeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self) -> List:
        return super().get_queryset()

    def get_serializer_class(self):
        return ProfileMergeSerializer

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
    def create(self, request: Request, *args, **kwargs) -> Response:
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)

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
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)
