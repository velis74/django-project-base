import importlib
import re
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
    change_password, logout, register, reset_password, send_reset_password_link, verify_email, verify_registration
)
from rest_registration.api.views.login import perform_login
from rest_registration.exceptions import LoginInvalid, UserNotFound
from rest_registration.settings import registration_settings
from rest_registration.utils.responses import get_ok_response


class LoginSerializer(serializers.Serializer):
    login = fields.CharField(required=True)
    password = fields.CharField(required=True)


class LoginViewSet(viewsets.ViewSet):
    serializer_class = LoginSerializer

    @extend_schema(
        description='Logs in the user with given username and password.',
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK'),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Bad request. Missing either one of parameters or wrong login or password.'
            )
        }
    )
    @action(detail=False, methods=['post'], url_name='login', authentication_classes=[], permission_classes=[])
    def login(self, request: Request) -> Response:
        serializer_class = registration_settings.LOGIN_SERIALIZER_CLASS
        serializer = serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        login_authenticator = registration_settings.LOGIN_AUTHENTICATOR
        try:
            user = login_authenticator(serializer.validated_data, serializer=serializer)
        except UserNotFound:
            raise LoginInvalid() from None

        extra_data = perform_login(request, user)

        try:
            extra_data.update({'sessionid': request.session.session_key})
        except:
            pass

        return get_ok_response(_("Login successful"), extra_data=extra_data)

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
        description='Logs out the user. Returns an error if the user is not authenticated. '
                    'If revoke_token is provided, revokes the given token for a given user. If the token is not  '
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
        description='Reset password through a link sent in email, given the signature and timestamp from the link.',
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
        description='Verify registration with signature. The endpoint will generate an e-mail with a confirmation URL '
                    'which the user should GET to confirm the account.',
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
    description='Register new user. The endpoint will generate an e-mail with a confirmation URL which the newly '
                'registered user should GET to activate the newly created account.',
    responses={
        status.HTTP_200_OK: OpenApiResponse(description='OK', response=RegisterReturnSerializer),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description=re.sub(r' +', ' ', """
                   There was a problem with the data. Response contains a JSON object showing validation errors per
                   field. JSON object keys are field names with issues, containing a list of issues and a
                   "non_field_errors" field containing errors that do not apply to a single field. Example: {
                     "password": [
                       "The password is too similar to the username.",
                       "This password is too short. It must contain at least 8 characters."
                     ],
                     "password_confirm": [
                       "Passwords don't match"
                     ],
                     "non_field_errors": []
                   }""".replace('\n', ' '))
        ),
    }
)
class RegisterViewSet(viewsets.ViewSet):
    serializer_class = RegisterSerializer

    @action(detail=False, methods=['post'], url_path='register', url_name='register')
    def register(self, request: Request) -> Response:
        return register(request._request)
