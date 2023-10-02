from django.db import models
from django.db.models import fields
from taggit.managers import TaggableManager

from django_project_base.auth.models import BasePermission, BaseRole
from django_project_base.base.models import (
    BaseInvite,
    BaseMergeUserGroup,
    BaseProfile,
    BaseProject,
    BaseProjectMember,
    BaseProjectSettings,
    BaseTag,
    DpbTaggedItemThrough,
)


class UserProfile(BaseProfile):
    pass


class Project(BaseProject):
    owner = models.ForeignKey(UserProfile, related_name="user_profiles", on_delete=models.CASCADE)


class ProjectMember(BaseProjectMember):
    pass


class DemoProjectTag(BaseTag):
    content = models.CharField(max_length=20, null=True, blank=True)

    class Meta(BaseTag.Meta):
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class DpbTaggedItemThroughDemo(DpbTaggedItemThrough):
    pass


class Apartment(models.Model):
    number = fields.IntegerField()
    tags = TaggableManager(through=DpbTaggedItemThroughDemo, related_name="apartment_tags")


class MergeUserGroup(BaseMergeUserGroup):
    pass


class Role(BaseRole):
    pass


class Permission(BasePermission):
    pass


class ProjectSettings(BaseProjectSettings):
    pass


class ProjectInvite(BaseInvite):
    pass
