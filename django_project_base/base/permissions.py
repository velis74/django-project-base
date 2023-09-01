from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


def can_user_hijack_another_user(hijacker, hijacked):
    # TODO: should this be solved by using roles
    return hijacker.is_authenticated and (hijacker.is_superuser or hijacker.is_staff)
