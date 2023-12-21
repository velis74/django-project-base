import swapper

from django.contrib.auth.models import Group, Permission


class BaseRole(Group):
    # Right now our role does not do anything more than Django's
    class Meta:
        abstract = True


class Role(BaseRole):
    # Right now our role does not do anything more than Django's
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "Role")


class BasePermission(Permission):
    # Right now our permission does not do anything more than Django's
    class Meta:
        abstract = True


class Permission(BasePermission):
    # Right now our permission does not do anything more than Django's
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "Permission")
