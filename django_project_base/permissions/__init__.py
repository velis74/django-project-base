import functools

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission as DRFBasePermission
from rest_framework.settings import api_settings


def check_permission(permission: str):
    def check(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            request = args[1]
            # view_set = args[0]

            def make_check_permission(permission, request) -> bool:
                # user = request.user
                # project = request.selected_project
                return True

            if make_check_permission(permission, request):
                return func(*args, **kwargs)

            raise PermissionDenied

        return wrap

    return check


class BasePermissions(DRFBasePermission):
    def has_permission(self, request, view):
        default_permission_classes = getattr(api_settings, "DEFAULT_PERMISSION_CLASSES", [])
        return all(
            [permission_class().has_permission(request, view) for permission_class in default_permission_classes]
        )
