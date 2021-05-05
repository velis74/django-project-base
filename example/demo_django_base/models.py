from django.db import models
from django.db.models import fields
from django_project_base.base.models import BaseProfile, BaseProject, BaseTag
from taggit.managers import TaggableManager
from taggit.models import GenericTaggedItemBase
from django.core.cache import cache


class ProfilesQuerySet(models.QuerySet):
    def update(self, **kwargs):
        res = super(ProfilesQuerySet, self).update(**kwargs)
        for profile in self:
            cache.delete(profile.django_user_cache_id())
        return res


class UserProfile(BaseProfile):
    """Use this only for enabling cache clear for bulk update"""
    objects = ProfilesQuerySet.as_manager()


class Project(BaseProject):
    owner = models.ForeignKey(UserProfile, related_name='user_profiles', on_delete=models.CASCADE)


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
