import importlib
from typing import List

from django.utils.translation import ugettext_lazy as _
from django_project_base.constants import ACCOUNT_URL_PREFIX
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import fields, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_registration.api.views import (
    change_password, login, logout, register, reset_password, send_reset_password_link, verify_email,
    verify_registration
)


class LoginSerializer(serializers.Serializer):
    login = fields.CharField(required=True)
    password = fields.CharField(required=True)


class LoginViewSet(viewsets.ViewSet):
    serializer_class = LoginSerializer

    @extend_schema(
        description='Logs in the user via given username and password.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Bad request. Missing either one of parameters or wrong login or password.'
            )
        }
    )
    @action(detail=False, methods=['post'], url_name='login')
    def login(self, request: Request) -> Response:
        return login(request._request)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK'),
        }
    )
    @action(detail=False, methods=['get'], url_path='social-auth-providers', url_name='social-auth-providers',
            permission_classes=[], authentication_classes=[])
    def social_auth_providers(self, request: Request) -> Response:
        """ Get enabled social auth providers configuration. """
        config: List[dict] = []
        from django.conf import settings
        locals()['social_core'] = importlib.import_module('social_core')
        authentication_backends: iter = filter(lambda b: 'social_core' in b, settings.AUTHENTICATION_BACKENDS)
        existing_settings: list = list(
            map(lambda e: e.lower(), filter(lambda s: s.lower().startswith('social_auth_'), dir(settings))))
        for auth_bckend in authentication_backends:
            __import__('.'.join(auth_bckend.split('.')[:3]))
            name: str = getattr(eval(auth_bckend), 'name')
            search_query: str = next(iter(name.split('-'))).lower()
            search_results: list = list(
                filter(lambda d: search_query in d and (d.endswith('_key') or d.endswith('_secret')),
                       existing_settings))
            if search_results:
                config.append({
                    'name': name,
                    'title': '%s %s' % (_('Login with'), search_query.lower().title()),
                    'url': '/%s/social/login/%s/' % (ACCOUNT_URL_PREFIX, name),
                })
        return Response(config)


class LogoutSerializer(serializers.Serializer):
    revoke_token = fields.BooleanField(required=False)


class LogoutViewSet(viewsets.ViewSet):
    serializer_class = LogoutSerializer

    @extend_schema(
        description='Logs out the user. returns an error if the user is not authenticated. '
                    'If revoke_token is selected, revokes the given token for a given user. If the token is not  '
                    'provided, revoke all tokens for given user. ',
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK'),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Not authorised'),
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
            status.HTTP_200_OK: OpenApiResponse(description='OK'),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Not allowed'),
        }
    )
    @action(detail=False, methods=['post'], url_path='change-password', url_name='change-password',
            permission_classes=[IsAuthenticated])
    def change_password(self, request: Request) -> Response:
        return change_password(request._request)


class ResetPasswordSerializer(serializers.Serializer):
    user_id = fields.CharField(required=True)
    timestamp = fields.CharField(required=True)
    signature = fields.CharField(required=True)
    password = fields.CharField(required=True)


class ResetPasswordViewSet(viewsets.ViewSet):
    serializer_class = ResetPasswordSerializer

    @extend_schema(
        description='Reset password, given the signature and timestamp from the link.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK Reset link sent'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Bad request.'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Reset password verification disabled'),
        }
    )
    @action(detail=False, methods=['post'], url_path='reset-password', url_name='reset-password')
    def reset_password(self, request: Request) -> Response:
        return reset_password(request._request)

    @extend_schema(
        description='Verify email via signature.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK Email verified successfully'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Bad request')
        }
    )
    @action(detail=False, methods=['post'], url_path='verify-email', url_name='verify-email')
    def verify_email(self, request: Request) -> Response:
        return verify_email(request._request)


class VerifyRegistrationSerializer(serializers.Serializer):
    user_id = fields.CharField(required=True)
    timestamp = fields.IntegerField(required=True)
    signature = fields.CharField(required=True)


class VerifyRegistrationViewSet(viewsets.ViewSet):
    serializer_class = VerifyRegistrationSerializer()

    @extend_schema(
        description='Verify registration via signature. The user who wants to register itself sends AJAX POST request '
                    'to register/ endpoint. The register endpoint will generate an e-mail which will contain an URL '
                    'which the newly registered user should click to activate account.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK', response=ResetPasswordSerializer),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Bad request')
        }
    )
    @action(detail=False, methods=['post'], url_path='verify_registration', url_name='verify-registration')
    def verify_registration(self, request: Request) -> Response:
        return verify_registration(request._request)


class SendResetPasswordLinkSerializer(serializers.Serializer):
    login = fields.CharField(required=True)


class SendResetPasswordLinkViewSet(viewsets.ViewSet):
    serializer_class = SendResetPasswordLinkSerializer()

    @extend_schema(
        description='Send email with reset password link.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK Reset link sent',
                                                response=SendResetPasswordLinkSerializer()),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Bad request'),
            404: 'Reset password verification disabled'
        }
    )
    @action(detail=False, methods=['post'], url_path='send-reset-password-link', url_name='send-reset-password-link')
    def send_reset_password_link(self, request: Request) -> Response:
        return send_reset_password_link(request._request)


class RegisterSerializer(serializers.Serializer):
    username = fields.CharField(required=True)
    email = fields.CharField(required=True)
    password = fields.CharField(required=True)
    password_confirm = fields.CharField(required=True)
    first_name = fields.CharField(required=False)
    last_name = fields.CharField(required=False)


class RegisterReturnSerializer(serializers.Serializer):
    id = fields.IntegerField()
    username = fields.CharField()
    email = fields.CharField()
    first_name = fields.CharField()
    last_name = fields.CharField()


@extend_schema(
    description='Register new user. The user who wants to register itself sends AJAX POST request to register/ '
                'endpoint. The register/ endpoint will generate an e-mail which will contain an URL which the newly '
                'registered user should click to activate account. ',
    responses={
        status.HTTP_200_OK: OpenApiResponse(description='OK', response=RegisterReturnSerializer),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description='BadRequest. Responce cam be either of: "This password is too short. It must contain at least'
                        ' 8 characters.","The password is too similar to the username." or  "A user with that username'
                        ' already exists."'
        ),
    }
)
class RegisterViewSet(viewsets.ViewSet):
    serializer_class = RegisterSerializer

    @action(detail=False, methods=['post'], url_path='register', url_name='register')
    def register(self, request: Request) -> Response:
        return register(request._request)
