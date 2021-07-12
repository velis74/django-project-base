from rest_framework.routers import DefaultRouter

from .rest import (
    ChangePasswordViewSet, LoginViewSet, LogoutViewSet, RegisterViewSet, ResetPasswordViewSet,
    SendResetPasswordLinkViewSet, VerifyRegistrationViewSet
)

accounts_router = DefaultRouter(trailing_slash=True)

accounts_router.register(r'', LoginViewSet, basename='account')
accounts_router.register(r'', LogoutViewSet, basename='account')
accounts_router.register(r'', ChangePasswordViewSet, basename='account')
accounts_router.register(r'', ResetPasswordViewSet, basename='account')
accounts_router.register(r'', RegisterViewSet, basename='account')
accounts_router.register(r'', SendResetPasswordLinkViewSet, basename='account')
accounts_router.register(r'', VerifyRegistrationViewSet, basename='account')
