from dynamicforms.routers import DFRouter

from django_project_base.account.rest.invite import ProjectUserInviteViewSet
from django_project_base.account.rest.profile import ProfileViewSet

profile_router = DFRouter(trailing_slash=False)
profile_router.register(r"profile", ProfileViewSet, basename="profile-base-project")
profile_router.register(r"project-user-invite", ProjectUserInviteViewSet, basename="project-user-invite")
