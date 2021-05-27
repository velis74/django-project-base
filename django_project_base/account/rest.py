import importlib
from typing import List

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_registration.api.views import change_password, login, logout, reset_password, send_reset_password_link, \
    verify_email, verify_registration
from django.utils.translation import ugettext_lazy as _

from django_project_base.constants import ACCOUNT_URL_PREFIX


class AccountViewSet(viewsets.ViewSet):

    @extend_schema(
        parameters=[
            OpenApiParameter(name='login', description='Username', required=True, type=str),
            OpenApiParameter(name='password', description='Password', required=True, type=str)
        ],
        responses={
            200: OpenApiResponse(description='OK'),
            400: OpenApiResponse(
                description='Bad request. Missing either one of parameters or wrong login or password.'
            )
        }
    )
    @action(detail=False, methods=['post'], url_name='login')
    def login(self, request: Request) -> Response:
        """ Logs in the user via given username and password. """
        return login(request._request)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='revoke_token', description='Should revoke token', required=False, type=bool)
        ],
        responses={
            200: OpenApiResponse(description='OK'),
            403: OpenApiResponse(description='Not authorised'),
        }

    )
    @action(detail=False, methods=['post'], url_name='logout')
    def logout(self, request: Request) -> Response:
        """ Logs out user."""
        return logout(request._request)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='old_password', description='Old password', required=True, type=str),
            OpenApiParameter(name='password', description='Password', required=True, type=str),
            OpenApiParameter(name='confirm_password', description='Confirm password', required=True, type=str)
        ],
        responses={
            200: OpenApiResponse(description='OK'),
            400: OpenApiResponse(description='Test'),
            403: OpenApiResponse(description='Bad request'),
        }
    )
    @action(detail=False, methods=['post'], url_path='change-password', url_name='change-password')
    def change_password(self, request: Request) -> Response:
        """ Change the user password. """
        return change_password(request._request)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='user_id', description='User id', required=True, type=str),
            OpenApiParameter(name='timestamp', description='Timestamp', required=True),
            OpenApiParameter(name='signature', description='Signature', required=True, type=str),
            OpenApiParameter(name='password', description='Password', required=True, type=str),
        ],
        responses={
            200: OpenApiResponse(description='OK'),
        }
    )
    @action(detail=False, methods=['post'], url_path='reset-password', url_name='reset-password')
    def reset_password(self, request: Request) -> Response:
        """ Reset password, given the signature and timestamp from the link. """
        return reset_password(request._request)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='login', description='Username', required=True, type=str),

        ],
        responses={
            200: OpenApiResponse(description='OK'),
            400: OpenApiResponse(description='???'),
        }
    )
    @action(detail=False, methods=['post'], url_path='send-reset-password-link', url_name='send-reset-password-link')
    def send_reset_password_link(self, request: Request) -> Response:
        """ Send email with reset password link. """
        return send_reset_password_link(request._request)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='user_id', description='User id', required=True, type=str),
            OpenApiParameter(name='timestamp', description='Timestamp', required=True),
            OpenApiParameter(name='signature', description='Signature', required=True, type=str),
            OpenApiParameter(name='password', description='Password', required=True, type=str),
        ],
        responses={
            200: OpenApiResponse(description='OK'),
        }
    )
    @action(detail=False, methods=['post'], url_path='verify-email', url_name='verify-email')
    def verify_email(self, request: Request) -> Response:
        """ Verify email via signature. """
        return verify_email(request._request)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='user_id', description='User id', required=True, type=str),
            OpenApiParameter(name='timestamp', description='Timestamp', required=True),
            OpenApiParameter(name='signature', description='Signature', required=True, type=str),
            OpenApiParameter(name='password', description='Password', required=True, type=str),
        ],
        responses={
            200: OpenApiResponse(description='OK'),
        }
    )
    @action(detail=False, methods=['post'], url_path='verify-registration', url_name='verify-registration')
    def verify_registration(self, request: Request) -> Response:
        """ Verify registration via signature. """
        return verify_registration(request._request)

    @extend_schema(
        responses={
            200: OpenApiResponse(description='OK'),
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
