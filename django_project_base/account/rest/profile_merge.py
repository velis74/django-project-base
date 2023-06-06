from typing import List

import swapper
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from dynamicforms.template_render.layout import Column, Layout, Row
from dynamicforms.template_render.responsive_table_layout import ResponsiveTableLayout, ResponsiveTableLayouts
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

    class Meta:
        model = swapper.load_model("django_project_base", "Profile")
        exclude = ("user_permissions", "password_invalid")
        layout = Layout(
            Row(Column("username"), Column("password")),
            Row(Column("first_name"), Column("last_name")),
            Row("reverse_full_name_order"),
            Row("email"),
            Row("phone_number"),
            Row("language"),
            Row("avatar"),
            columns=2,
            size="large",
        )
        responsive_columns = ResponsiveTableLayouts(
            auto_generate_single_row_layout=True,
            layouts=[
                ResponsiveTableLayout(auto_add_non_listed_columns=True),
                ResponsiveTableLayout("full_name", "email", auto_add_non_listed_columns=False),
            ],
        )


@extend_schema_view(
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
)
class ProfileMergeViewSet(ProfileViewSet):
    serializer_class = ProfileMergeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self) -> List:
        return []

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
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)

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
