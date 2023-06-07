from django.conf import settings
from django.utils.module_loading import import_string


class MergeUsersService:
    def handle(self, **kwargs):
        if handler_function := getattr(settings, "MERGE_USERS_HANDLER", ""):
            user = kwargs.get("user")
            from example.demo_django_base.models import MergeUserGroup

            group = MergeUserGroup.objects.filter(users__icontains=user.pk).first()
            if user and group:
                import_string(handler_function)(user=user, all_users=group.users)
