from dynamicforms.routers import DFRouter

from django_project_base.account.rest.account import (
    AdminAddUserViewSet,
    ChangePasswordViewSet,
    LogoutViewSet,
    RegisterViewSet,
    SocialAuthProvidersViewSet,
    VerifyRegistrationViewSet,
)
from django_project_base.account.rest.impersonate import ImpersonateUserViewset
from django_project_base.account.rest.invite import ProjectUserInviteViewSet
from django_project_base.account.rest.login import LoginViewset
from django_project_base.account.rest.profile import ProfileViewSet, ProjectsProfileSearchViewSet
from django_project_base.account.rest.profile_merge import ProfileMergeViewSet
from django_project_base.account.rest.reset_password import (
    InvalidatePasswordAdminViewSet,
    ResetPasswordViewSet,
    SendResetPasswordLinkViewSet,
)

accounts_router = DFRouter(trailing_slash=True)

accounts_router.register(r"", SocialAuthProvidersViewSet, basename="account")
accounts_router.register(r"change-password", ChangePasswordViewSet, basename="change-password")
accounts_router.register(
    r"admin-invalidate-password", InvalidatePasswordAdminViewSet, basename="admin-invalidate-password"
)
accounts_router.register(r"admin-add-user", AdminAddUserViewSet, basename="admin-add-user")
accounts_router.register(r"", ResetPasswordViewSet, basename="account-reset-pass")
accounts_router.register(r"", RegisterViewSet, basename="account-register")
accounts_router.register(r"", SendResetPasswordLinkViewSet, basename="account-send-reset-pwd-link")
accounts_router.register(r"", VerifyRegistrationViewSet, basename="account-verify-registration")

profile_router = DFRouter(trailing_slash=False)
profile_router.register(r"profile", ProfileViewSet, basename="profile-base-project")
profile_router.register(r"profile-merge", ProfileMergeViewSet, basename="profile-merge-base-project")
profile_router.register_single_record(r"impersonate", ImpersonateUserViewset, basename="profile-base-impersonate-user")
profile_router.register_single_record(r"login", LoginViewset, basename="profile-base-login")
# Following line is for backwards compatibility. PBXs calls login with trailing slash
profile_router.register_single_record(r"login/", LoginViewset, basename="profile-base-login2")
profile_router.register(r"", LogoutViewSet, basename="account-logout")
profile_router.register(r"project-user-invite", ProjectUserInviteViewSet, basename="project-user-invite")
profile_router.register(r"projects-profile-search", ProjectsProfileSearchViewSet, basename="projects-profile-search")
