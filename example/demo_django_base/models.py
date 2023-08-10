from django.db import models
from django.db.models import fields
from taggit.managers import TaggableManager

from django_project_base.base.models import (
    BaseMergeUserGroup,
    BaseProfile,
    BaseProject,
    BaseProjectMember,
    BaseTag,
    DpbTaggedItemThrough,
)


class UserGroup(models.Model):
    name = models.CharField(max_length=64)


class UserProfile(BaseProfile):
    group = models.ForeignKey(UserGroup, null=True, on_delete=models.CASCADE)


class Project(BaseProject):
    owner = models.ForeignKey(UserProfile, related_name="user_profiles", on_delete=models.CASCADE)


class ProjectMember(BaseProjectMember):
    pass


class DemoProjectTag(BaseTag):
    content = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class DpbTaggedItemThroughDemo(DpbTaggedItemThrough):
    pass


class Apartment(models.Model):
    number = fields.IntegerField()
    tags = TaggableManager(through=DpbTaggedItemThroughDemo, related_name="apartment_tags")


class MergeUserGroup(BaseMergeUserGroup):
    pass
