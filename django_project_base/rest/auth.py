from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_registration.api.views import change_password, login, logout


class LoginViewset(viewsets.ViewSet):

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


class ChangePasswordViewset(viewsets.ViewSet):

    @extend_schema(
        parameters=[
            OpenApiParameter(name='old_password', description='Old password', required=True, type=str),
            OpenApiParameter(name='password', description='Password', required=True, type=str),
            OpenApiParameter(name='confirm_password', description='Confirm password', required=True, type=str)
        ],
        responses={
            200: OpenApiResponse(description='Test', response={OpenApiExample('Example 1')}),
            400: OpenApiResponse(description='Test', response={OpenApiExample(
                'Example 403',
                summary='Summary',
                description='Test',
                value="This password is too short. It must contain at least 8 characters.",
            )}),
            403: 'Test',
        }
    )
    @action(detail=False, methods=['post'], url_name='change-password')
    def change_password(self, request: Request) -> Response:
        """ Change the user password. """
        return change_password(request._request)
