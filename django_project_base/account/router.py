from rest_framework.routers import DefaultRouter

from django_project_base.account.rest.account import (
    ChangePasswordViewSet, LoginViewSet, LogoutViewSet, RegisterViewSet, ResetPasswordViewSet,
    SendResetPasswordLinkViewSet, VerifyRegistrationViewSet
)
from django_project_base.account.rest.impersonate import ImpersonateUserViewset
from django_project_base.account.rest.profile import ProfileViewSet
from django_project_base.rest_config import REST_API_CONFIG

accounts_router = DefaultRouter(trailing_slash=True)

accounts_router.register(r'%s' % REST_API_CONFIG.Account.Login.url, LoginViewSet,
                         basename=REST_API_CONFIG.Account.Login.basename)
accounts_router.register(r'%s' % REST_API_CONFIG.Account.Logout.url, LogoutViewSet,
                         basename=REST_API_CONFIG.Account.Logout.basename)
accounts_router.register(r'%s' % REST_API_CONFIG.Account.ChangePassword.url, ChangePasswordViewSet,
                         basename=REST_API_CONFIG.Account.ChangePassword.basename)
accounts_router.register(r'%s' % REST_API_CONFIG.Account.ResetPassword.url, ResetPasswordViewSet,
                         basename=REST_API_CONFIG.Account.ResetPassword.basename)
accounts_router.register(r'%s' % REST_API_CONFIG.Account.Register.url, RegisterViewSet,
                         basename=REST_API_CONFIG.Account.Register.basename)
accounts_router.register(r'%s' % REST_API_CONFIG.Account.ResetPasswordLink.url, SendResetPasswordLinkViewSet,
                         basename=REST_API_CONFIG.Account.ResetPasswordLink.basename)
accounts_router.register(r'%s' % REST_API_CONFIG.Account.VerifyRegistration.url, VerifyRegistrationViewSet,
                         basename=REST_API_CONFIG.Account.VerifyRegistration.basename)

profile_router = DefaultRouter(trailing_slash=False)
profile_router.register(r'%s' % REST_API_CONFIG.Profile.url, ProfileViewSet, basename=REST_API_CONFIG.Profile.basename)
profile_router.register(r'%s' % REST_API_CONFIG.Impersonate.url, ImpersonateUserViewset,
                        basename=REST_API_CONFIG.Impersonate.basename)
