from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import fields, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_registration.api.views import (
    change_password, login, logout, reset_password, send_reset_password_link, verify_email
)


class LoginSerializer(serializers.Serializer):
    login = fields.CharField(required=True)
    password = fields.CharField(required=True)


class LoginViewSet(viewsets.ViewSet):
    serializer_class = LoginSerializer

    @extend_schema(
        description='Logs in the user via given username and password.',
        responses={
            200: OpenApiResponse(description='OK'),
            400: OpenApiResponse(
                description='Bad request. Missing either one of parameters or wrong login or password.'
            )
        }
    )
    @action(detail=False, methods=['post'], url_name='login')
    def login(self, request: Request) -> Response:
        return login(request._request)


class LogoutSerializer(serializers.Serializer):
    revoke_token = fields.BooleanField(required=False)


class LogoutViewSet(viewsets.ViewSet):
    serializer_class = LogoutSerializer

    @extend_schema(
        description='Logs out the user. returns an error if the user is not authenticated. '
                    'If revoke_token is selected, revokes the given token for a given user. If the token is not  '
                    'provided, revoke all tokens for given user. ',
        responses={
            200: OpenApiResponse(description='OK'),
            403: OpenApiResponse(description='Not authorised'),
        }

    )
    @action(detail=False, methods=['post'], url_name='logout', permission_classes=[IsAuthenticated])
    def logout(self, request: Request) -> Response:
        return logout(request._request)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = fields.CharField(required=True)
    password = fields.CharField(required=True)
    confirm_password = fields.CharField(required=True)


class ChangePasswordViewSet(viewsets.ViewSet):
    serializer_class = ChangePasswordSerializer

    @extend_schema(
        description='Change the user password.',
        responses={
            200: OpenApiResponse(description='OK'),
            403: OpenApiResponse(description='Bad request'),
        }
    )
    @action(detail=False, methods=['post'], url_path='change-password', url_name='change-password',
            permission_classes=[IsAuthenticated])
    def change_password(self, request: Request) -> Response:
        return change_password(request._request)


class ResetPasswordSerializer():
    user_id = fields.CharField(required=True)
    timestamp = fields.CharField(required=True)
    signature = fields.CharField(required=True)
    password = fields.CharField(required=True)


class ResetPasswordViewSet(viewsets.ViewSet):
    serializer_class = ResetPasswordSerializer

    @extend_schema(
        description='Reset password, given the signature and timestamp from the link.',
        responses={
            200: OpenApiResponse(description='OK'),
        }
    )
    @action(detail=False, methods=['post'], url_path='reset-password', url_name='reset-password',
            permission_classes=[IsAuthenticated])
    def reset_password(self, request: Request) -> Response:
        return reset_password(request._request)

    @extend_schema(
        description='Verify email via signature.',
        responses={
            200: OpenApiResponse(description='OK'),
        }
    )
    @action(detail=False, methods=['post'], url_path='verify-email', url_name='verify-email')
    def verify_email(self, request: Request) -> Response:
        return verify_email(request._request)


class SendResetPasswordLinkSerializer(serializers.Serializer):
    login = fields.CharField(required=True)


class SendResetPasswordLinkViewSet(viewsets.ViewSet):
    serializer_class = SendResetPasswordLinkSerializer

    @extend_schema(
        description='Send email with reset password link.',
        responses={
            200: OpenApiResponse(description='OK'),
            400: OpenApiResponse(description='???'),
        }
    )
    @action(detail=False, methods=['post'], url_path='send-reset-password-link', url_name='send-reset-password-link')
    def send_reset_password_link(self, request: Request) -> Response:
        return send_reset_password_link(request._request)
