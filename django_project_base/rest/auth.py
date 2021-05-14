from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_registration.api.views import change_password, login, logout


class LoginViewset(viewsets.ViewSet):

    @extend_schema(
        parameters=[
            OpenApiParameter(name='login', description='Unique email address', required=True, type=str),
            OpenApiParameter(name='password', description='Password', required=True, type=str)
        ],
    )
    @action(detail=False, methods=['post'], url_name='login')
    def login(self, request: Request) -> Response:
        """ Logs in the user via given login and password. """
        return login(request._request)

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
