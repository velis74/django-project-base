from django.db import models
from django.db.models import fields
from taggit.managers import TaggableManager
from taggit.models import GenericTaggedItemBase

from django_project_base.base.models import BaseProfile, BaseProject, BaseProjectMember, BaseTag


class UserProfile(BaseProfile):
    pass


class Project(BaseProject):
    owner = models.ForeignKey(UserProfile, related_name="user_profiles", on_delete=models.CASCADE)


class ProjectMember(BaseProjectMember):
    pass


class DemoProjectTag(BaseTag):
    content = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


class TaggedItemThrough(GenericTaggedItemBase):
    tag = models.ForeignKey(
        DemoProjectTag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )


class Apartment(models.Model):
    number = fields.IntegerField()
    tags = TaggableManager(blank=True, through=TaggedItemThrough, related_name="apartment_tags")
