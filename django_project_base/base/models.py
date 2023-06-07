from typing import List

import svgwrite
import swapper
from django.conf import settings
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from taggit.models import TagBase

from django_project_base.base.fields import HexColorField


class BaseProject(models.Model):
    name = models.CharField(max_length=80, null=False, blank=False, db_index=True, verbose_name=_("Name"))
    slug = models.SlugField(max_length=80, null=False, blank=False, verbose_name=_("Slug"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    logo = models.FileField(null=True, blank=True, verbose_name=_("Logo"))
    owner = parent = models.ForeignKey(
        swapper.get_model_name("django_project_base", "Profile"), on_delete=models.CASCADE, verbose_name=_("Owner")
    )

    class Meta:
        abstract = True


class Project(BaseProject):
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "Project")


class BaseProfile(User):
    """
    User profile. We start with some easy common settings
    """

    bio = models.TextField(max_length=500, null=True, blank=True, verbose_name=_("Bio"))
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Phone number"))
    # This one will list all supported languages
    language = models.CharField(max_length=10, null=True, blank=True, verbose_name=_("Language"))
    # This one will list all supported themes
    theme = models.CharField(max_length=10, null=True, blank=True, verbose_name=_("Theme"))
    avatar = models.FileField(null=True, blank=True, verbose_name=_("Avatar"))
    reverse_full_name_order = models.BooleanField(null=True, blank=True, verbose_name=_("Reverse full name order"))
    delete_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Delete profile at"))
    password_invalid = models.BooleanField(default=False)

    def get_full_name(self, reverse_order: bool = False):
        # First we establish the natural order for this user
        if self.reverse_full_name_order is None:
            reversed_order = getattr(settings, "PROFILE_REVERSE_FULL_NAME_ORDER", False)
        else:
            reversed_order = self.reverse_full_name_order

        # Then we reverse this if requested for the method
        reversed_order = reversed_order ^ reverse_order

        first_name = self.first_name
        last_name = self.last_name
        if not (first_name or last_name):
            # if neither first nor last name were provided, we use the email address
            first_name = self.email

        if reversed_order:
            first_name, last_name = last_name, first_name

        return f"{first_name} {last_name}".strip()

    full_name = property(lambda self: self.get_full_name())
    full_name_reverse = property(lambda self: self.get_full_name(True))

    def get_users(self):
        objects_all = BaseProfile.objects
        return objects_all

    users = property(lambda self: self.get_users())

    class Meta:
        abstract = True


class Profile(BaseProfile):
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "Profile")


# noinspection PyUnusedLocal
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = swapper.load_model("django_project_base", "Profile")
        profile(user_ptr=instance).save_base(raw=True)


class BaseProjectMember(models.Model):
    project = models.ForeignKey(
        swapper.get_model_name("django_project_base", "Project"),
        on_delete=models.CASCADE,
        verbose_name=_("Project"),
        related_name="members",  # the name is just reversed: you seek members from the project
    )
    member = models.ForeignKey(
        swapper.get_model_name("django_project_base", "Profile"),
        on_delete=models.CASCADE,
        verbose_name=_("Owner"),
        related_name="projects",  # the name is just reversed: you seek projects this member belongs to
    )

    # role = models.ForeignKey()  # TODO: we don't have role support yet

    class Meta:
        abstract = True


class ProjectMember(BaseProjectMember):
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "ProjectMember")


class BaseTag(TagBase):
    color = HexColorField(verbose_name=_("Color"))
    # icon if char for now # todo: what will be used for icon
    icon = models.CharField(max_length=10, null=True, blank=True, verbose_name=_("Icon"))
    project = models.ForeignKey(
        settings.DJANGO_PROJECT_BASE_PROJECT_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Project"),
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.slugify(self.name)
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def get_background_svg_for_tags(tags: List["BaseTag"]) -> str:
        dwg = svgwrite.Drawing()
        dwg.viewbox(width=200, height=200)
        tricolor_gradient = dwg.linearGradient((0, 0), (1, 1))
        dwg.defs.add(tricolor_gradient)
        color_added_flag: bool = True
        for i, t in enumerate(tags):
            if t.color:
                tricolor_gradient.add_stop_color(i / len(tags), t.color)
                t.color = True
        if not color_added_flag:
            return ""
        dwg.add(dwg.rect((10, 70), (50, 50), fill=tricolor_gradient.get_paint_server(default="currentColor")))
        return '<?xml version="1.0" encoding="utf-8" ?>\n' + dwg.tostring()

    class Meta(TagBase.Meta):
        abstract = True


class BaseMergeUserGroup(models.Model):
    users = models.CharField(max_length=1024, null=False, validators=(validate_comma_separated_integer_list,))

    class Meta:
        abstract = True


@receiver(user_logged_in)
def user_logged_in(*args, **kwargs):
    from django_project_base.account.service.merge_users_service import MergeUsersService

    MergeUsersService().handle(**kwargs)
