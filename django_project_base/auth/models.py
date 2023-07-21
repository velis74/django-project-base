import swapper
from django.contrib.auth import models


class BaseRole(models.Group):
    # Right now our role does not do anything more than Django's
    pass


class Role(BaseRole):
    # Right now our role does not do anything more than Django's
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "Role")


class BasePermission(models.Permission):
    # Right now our permission does not do anything more than Django's
    pass


class Permission(BasePermission):
    # Right now our permission does not do anything more than Django's
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "Permission")
