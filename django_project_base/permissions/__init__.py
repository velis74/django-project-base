from rest_framework.permissions import BasePermission as DRFBasePermission
from rest_framework.settings import api_settings


class BasePermissions(DRFBasePermission):
    def has_permission(self, request, view):
        default_permission_classes = getattr(api_settings, "DEFAULT_PERMISSION_CLASSES", [])
        return all(
            [permission_class().has_permission(request, view) for permission_class in default_permission_classes]
        )


def can_user_hijack_another_user(hijacker, hijacked):
    # TODO: should this be solved by using roles
    return hijacker.is_authenticated and (hijacker.is_superuser or hijacker.is_staff)
