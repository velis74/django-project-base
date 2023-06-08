from typing import Optional

from django.conf import settings
from django.utils.module_loading import import_string


class MergeUsersService:
    def handle(self, **kwargs):
        if handler_function := getattr(settings, "MERGE_USERS_HANDLER", "") and kwargs.get("user"):
            user = kwargs["user"]
            group = self._find_group(user)
            if group:
                import_string(handler_function)(user=user, all_users=group.users)
                group.delete()

    def _find_group(self, user: "UserModel") -> Optional["MergeUserGroup"]:  # noqa:  F821
        from example.demo_django_base.models import MergeUserGroup

        return next(
            iter([group for group in MergeUserGroup.objects.all() if str(user.pk) in group.users.split(",")]), None
        )
