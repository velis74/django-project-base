from django_project_base.base.rest.router import Router as ProjectBaseRouter

from .rest import (
    ChangePasswordViewSet, LoginViewSet, LogoutViewSet, RegisterViewSet, ResetPasswordViewSet,
    SendResetPasswordLinkViewSet
)

accounts_router = ProjectBaseRouter(trailing_slash=True)

accounts_router.register(r'', LoginViewSet, basename='account')
accounts_router.register(r'', LogoutViewSet, basename='account')
accounts_router.register(r'', ChangePasswordViewSet, basename='account')
accounts_router.register(r'', ResetPasswordViewSet, basename='account')
accounts_router.register(r'', RegisterViewSet, basename='account')
accounts_router.register(r'', SendResetPasswordLinkViewSet, basename='account')
