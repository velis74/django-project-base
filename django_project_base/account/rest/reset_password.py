import json

import swapper
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiTypes
from dynamicforms import fields as df_fields, serializers as df_serializers, viewsets as df_viewsets
from dynamicforms.action import Actions
from rest_framework import fields, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_registration.api.views import reset_password, send_reset_password_link, verify_email
from rest_registration.exceptions import UserNotFound
from rest_registration.settings import registration_settings

from django_project_base.account.constants import RESET_USER_PASSWORD_VERIFICATION_CODE


class ResetPasswordSerializer(serializers.Serializer):
    user_id = fields.CharField(required=True)
    timestamp = fields.CharField(required=True)
    signature = fields.CharField(required=True)
    password = fields.CharField(required=True)


class ResetPasswordCodeSerializer(serializers.Serializer):
    user_id = fields.CharField(required=True)
    code = fields.CharField(required=True)

    def validate_code(self, value) -> str:
        if value and value == cache.get(RESET_USER_PASSWORD_VERIFICATION_CODE + str(self.initial_data.get("user_id"))):
            return value
        raise ValidationError("Invalid code")


class ResetPasswordViewSet(viewsets.ViewSet):
    serializer_class = ResetPasswordSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        description="Reset password through a link sent in email, given the signature and timestamp from the link.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK Reset link sent"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Bad request."),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Reset password verification disabled"),
        },
    )
    @action(detail=False, methods=["post"], url_path="reset-password", url_name="reset-password")
    def reset_password(self, request: Request) -> Response:
        code_ser = ResetPasswordCodeSerializer(
            data=json.loads(request._request.body.decode()), context=dict(request=request)
        )
        code_ser.is_valid(raise_exception=True)
        response = reset_password(request._request)
        cache.delete(RESET_USER_PASSWORD_VERIFICATION_CODE + str(code_ser["user_id"]))
        return response

    @extend_schema(
        description="Verify email via signature.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK Email verified successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Bad request"),
        },
    )
    @action(detail=False, methods=["post"], url_path="verify-email", url_name="verify-email")
    def verify_email(self, request: Request) -> Response:
        return verify_email(request._request)


class ResetPasswordAdminSerializer(df_serializers.Serializer):
    template_context = dict(
        url_reverse="admin-invalidate-password", dialog_classes="modal-lg", dialog_header_classes="bg-info"
    )
    form_titles = {
        "table": "",
        "new": _("Invalidate password"),
        "edit": "",
    }

    user_id = df_fields.IntegerField(required=True, help_text=_("Target user id"))

    actions = Actions()


@extend_schema_view(
    retrieve=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH, enum=["new"])]),
)
class InvalidatePasswordAdminViewSet(df_viewsets.SingleRecordViewSet):
    serializer_class = ResetPasswordAdminSerializer

    permission_classes = (IsAuthenticated, IsAdminUser)  # TODO: permission should be based on project role

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        request._dont_enforce_csrf_checks = True
        return request

    def new_object(self):
        return dict(user_id="")

    @extend_schema(
        description="Marks the user password to be changed."
        "When user logs to an app UI user is shown change password dialog.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    def create(self, request: Request) -> Response:
        self.serializer_class(data=request.data).is_valid(raise_exception=True)
        profile_obj = get_object_or_404(
            swapper.load_model("django_project_base", "Profile"), user_ptr_id=request.data.get("user_id")
        )
        profile_obj.password_invalid = True
        profile_obj.save(update_fields=["password_invalid"])
        return Response()


class SendResetPasswordLinkSerializer(serializers.Serializer):
    login = fields.CharField(required=True)


class SendResetPasswordLinkViewSet(viewsets.ViewSet):
    serializer_class = SendResetPasswordLinkSerializer()
    permission_classes = (AllowAny,)

    @extend_schema(
        description="Send email with reset password link.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="OK Reset link sent", response=SendResetPasswordLinkSerializer()
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Bad request"),
            status.HTTP_404_NOT_FOUND: "Reset password verification disabled",
        },
    )
    @action(detail=False, methods=["post"], url_path="send-reset-password-link", url_name="send-reset-password-link")
    def send_reset_password_link(self, request: Request) -> Response:
        try:
            req_data = request._request.body
            send_reset_password_link(request._request)
            reset_data = registration_settings.RESET_PASSWORD_VERIFICATION_EMAIL_SENDER(
                request=request,
                user=registration_settings.SEND_RESET_PASSWORD_LINK_USER_FINDER(json.loads(req_data.decode())),
                send=True,
            )
            return Response(reset_data)
        except UserNotFound:
            return Response()
        except Exception as e:
            raise e
