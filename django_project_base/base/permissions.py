from rest_framework.permissions import BasePermission, SAFE_METHODS

from django_project_base.account.middleware import ProjectNotSelectedError
from django_project_base.base.models import BaseProfile, BaseProject


class IsSuperUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


def can_user_hijack_another_user(hijacker, hijacked):
    # TODO: should this be solved by using roles
    return hijacker.is_authenticated and (hijacker.is_superuser or hijacker.is_staff)


def project_is_selected(project: BaseProject) -> bool:
    try:
        project.get_deferred_fields()  # force immediate LazyObject evaluation
    except ProjectNotSelectedError:
        return False
    return True


def is_authenticated(user: BaseProfile) -> bool:
    return bool(user and user.is_authenticated)


def is_project_member(user: BaseProfile, project: BaseProject) -> bool:
    return (
        is_authenticated(user)
        and project_is_selected(project)
        and (project.members.filter(member=user).exists() or is_project_owner(user, project))
    )


def is_project_owner(user: BaseProfile, project: BaseProject) -> bool:
    return is_authenticated(user) and project_is_selected(project) and user == project.owner


def is_superuser(user: BaseProfile) -> bool:
    return is_authenticated(user) and user.is_superuser

def is_staff(user: BaseProfile) -> bool:
    return is_authenticated(user) and user.is_staff


class IsProjectOwner(BasePermission):
    """
    Allows access only to project owners.
    """

    def has_permission(self, request, view):
        return is_superuser(request.user) or is_project_owner(request.user, request.selected_project)


class IsProjectMember(BasePermission):
    """
    Allows access only to project owners.
    """

    def has_permission(self, request, view):
        return is_superuser(request.user) or is_project_member(request.user, request.selected_project)


class IsProjectOwnerOrMemberReadOnly(BasePermission):
    """
    Allows access only to project owners.
    """

    def has_permission(self, request, view):
        from django_project_base.account.rest.project_profiles import ProjectProfilesViewSet

        if isinstance(view, ProjectProfilesViewSet):
            # this is a special case for user accounts: any user may write to their own account from anywhere
            # so if the user is trying to access their own account, we allow it, otherwise we run the default check
            try:
                instance = view.get_object()
                if instance == request.user:
                    return True
            except AssertionError:
                # will except in view.get_object() when the method is not PUT, PATCH, RETRIEVE
                pass

        return (
            is_superuser(request.user)
            or is_project_owner(request.user, request.selected_project)
            or ((request.method in SAFE_METHODS) and is_project_member(request.user, request.selected_project))
        )


class CreateAny(BasePermission):
    """
    Allows POST / create to anyone
    """

    def has_permission(self, request, view):
        return request.method == "POST"


class IsProjectOwnerOrReadOnly(BasePermission):
    """
    Allows access only to project owners.
    """

    def has_permission(self, request, view):
        return (
            is_superuser(request.user)
            or is_project_owner(request.user, request.selected_project)
            or (request.method in SAFE_METHODS)
        )


class IsProjectMemberOrAuthenticatedReadOnly(BasePermission):
    """
    Allows access only to project owners.
    """

    def has_permission(self, request, view):
        return is_project_member(request.user, request.selected_project) or (
            is_authenticated(request.user) and (request.method in SAFE_METHODS)
        )
