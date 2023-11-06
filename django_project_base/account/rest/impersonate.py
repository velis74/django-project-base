from django.contrib.auth import get_user_model
from django.db.models import Model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_field,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)
from dynamicforms import fields, serializers, viewsets
from dynamicforms.action import Actions, FormButtonAction, FormButtonTypes
from hijack.helpers import login_user, release_hijack
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

import django_project_base.base.fields


class ImpersonateRequestSerializer(serializers.Serializer):
    """
    Impersonation options. Fill out any of the fields to identify the impersonated user
    """

    id = fields.IntegerField(required=False, label=_("User ID"))
    email = fields.EmailField(required=False, label=_("User email"))
    username = fields.CharField(required=False)


@extend_schema_field(OpenApiTypes.NONE)
class ImpersonateUserIdField(django_project_base.base.fields.UserRelatedField):
    pass


class ImpersonateUserDialogSerializer(serializers.Serializer):
    template_context = dict(
        url_reverse="profile-base-impersonate-user", url_reverse_kwargs=None, dialog_header_classes="bg-info"
    )
    form_titles = {"new": "Impersonate a user"}

    id = ImpersonateUserIdField(
        placeholder=_("Select a user to impersonate"), label=_("User"), required=False, allow_null=True
    )

    actions = Actions(
        FormButtonAction(btn_type=FormButtonTypes.CANCEL, name="cancel", label=_("Cancel")),
        FormButtonAction(btn_type=FormButtonTypes.SUBMIT, name="submit", label=_("Impersonate")),
        add_form_buttons=False,
    )


@extend_schema_view(
    retrieve=extend_schema(
        description="Retrieves dialog definition for impersonation dialog",
        parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH, enum=["new"])],
    ),
)
class ImpersonateUserViewset(viewsets.SingleRecordViewSet):
    serializer_class = ImpersonateUserDialogSerializer

    def new_object(self):
        return dict(id=None)

    # noinspection PyMethodMayBeStatic
    def __validate(self, req_data: dict) -> dict:
        ser: ImpersonateRequestSerializer = ImpersonateRequestSerializer(data=req_data)
        ser.is_valid(raise_exception=True)
        return ser.validated_data

    class ImpersonateUser(serializers.Serializer):
        id = fields.IntegerField(required=True, help_text=_("Target user pk"))

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Forbidden"),
        },
        description="Logout as another user",
    )
    @permission_classes([IsAuthenticated])
    def destroy(self, request: Request) -> Response:
        release_hijack(request)
        return Response()

    @extend_schema(exclude=True)
    @permission_classes([IsAdminUser])
    def update(self, request: Request, *args, **kwargs) -> Response:
        self._hijack(request=request)
        return Response()

    def _hijack(self, request: Request):
        validated_data: dict = self.__validate(request.data)
        hijacked_user: Model = get_object_or_404(get_user_model(), **validated_data)
        if request.user == hijacked_user:
            raise PermissionDenied(_("Impersonating self is not allowed"))
        login_user(request, hijacked_user)

    @extend_schema(
        request=ImpersonateUser,
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Forbidden. You do not have permission to perform this action or "
                "Impersonating self is not allowed"
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="User matching provided data not found"),
        },
        description="Login as another user and work on behalf of other user without having to know their credentials",
    )
    @permission_classes([IsAdminUser])
    def create(self, request: Request, *args, **kwargs) -> Response:
        self._hijack(request=request)
        return Response()
