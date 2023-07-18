import swapper
from django.contrib.auth import models


class Role(models.Group):
    # Right now our role does not do anything more than Django's
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "Role")


class Permission(models.Permission):
    # Right now our permission does not do anything more than Django's
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "Permission")
