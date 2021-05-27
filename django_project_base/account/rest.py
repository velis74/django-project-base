from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_registration.api.views import (
    change_password, login, logout, reset_password, send_reset_password_link, verify_email, verify_registration
)


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
