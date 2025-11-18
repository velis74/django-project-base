import uuid

from typing import List

import svgwrite
import swapper

from django.conf import settings
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from rest_framework.exceptions import ErrorDetail, PermissionDenied
from taggit.models import GenericTaggedItemBase, TagBase

from django_project_base.base.fields import HexColorField


class BaseProject(models.Model):
    name = models.CharField(max_length=80, null=False, blank=False, db_index=True, verbose_name=_("Name"))
    slug = models.SlugField(max_length=80, null=False, blank=False, unique=True, verbose_name=_("Slug"))
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

        first_name = self.first_name or ""
        last_name = self.last_name or ""
        if not (first_name or last_name):
            # if neither first nor last name were provided, we use the email address
            first_name = self.username or self.email or ""

        if reversed_order:
            first_name, last_name = last_name, first_name

        return f"{first_name.strip()} {last_name.strip()}".strip()

    full_name = property(lambda self: self.get_full_name())
    full_name_reverse = property(lambda self: self.get_full_name(True))

    @property
    def is_new_user(self):
        return self.password_invalid and not self.password

    def get_users(self):
        objects_all = BaseProfile.objects
        return objects_all

    @property
    def first_project(self):
        if "projects" in getattr(self, "_prefetched_objects_cache", []):
            # Če na prefetchanih podatkih delam order, first, itd... potem gre šeenkrat nabirati v bazo.
            for project in self.projects.all():
                return project
            return None
        else:
            return self.projects.first()

    users = property(lambda self: self.get_users())

    def __str__(self):
        return self.full_name

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

    @property
    def project_members_excluded_fields(self):
        return "id", "member", "project"

    @property
    def project_members_fields(self):
        fields_club = swapper.load_model("django_project_base", "ProjectMember")._meta.fields
        return [field for field in fields_club if field.name not in self.project_members_excluded_fields]

    @property
    def project_members_fields_names(self):
        return [field.name for field in self.project_members_fields]

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
    name = models.CharField(verbose_name=pgettext_lazy("A tag name", "name"), unique=False, max_length=100)
    slug = models.SlugField(
        verbose_name=pgettext_lazy("A tag slug", "slug"), unique=False, max_length=100, allow_unicode=True
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
        unique_together = [
            ["project", "name"],
            ["project", "slug"],
        ]


class DpbTaggedItemThrough(GenericTaggedItemBase):
    tag = models.ForeignKey(
        swapper.get_model_name("django_project_base", "Tag"),
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )
    # main_object actually states whether this tag is auto-generated. Used e.g. in UserGroups where a tag is always
    #   generated for a user group. The auto-generated ones have this flag set.
    main_object = models.BooleanField(default=False)

    class Meta(GenericTaggedItemBase.Meta):
        abstract = True


class Tag(BaseTag):
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "Tag")


class BaseMergeUserGroup(models.Model):
    users = models.CharField(max_length=1024, null=False, validators=(validate_comma_separated_integer_list,))
    created_by = models.PositiveIntegerField()
    project = models.ForeignKey(
        swapper.get_model_name("django_project_base", "Project"), on_delete=models.CASCADE, null=False
    )

    class Meta:
        abstract = True


# TODO: not sure this is even needed? why would anyone want to override this particular table?
class MergeUserGroup(BaseMergeUserGroup):
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "MergeUserGroup")


class ProjectSettingsQs(models.query.QuerySet):
    def delete(self):
        raise PermissionDenied


class BaseProjectSettings(models.Model):
    VALUE_TYPE_INTEGER = "integer"
    VALUE_TYPE_FLOAT = "float"
    VALUE_TYPE_BOOL = "bool"
    VALUE_TYPE_CHAR = "char"
    # custom means that there's a custom editor for this setting, so it needs to be hidden from the general editor
    VALUE_TYPE_CUSTOM = "custom"

    VALUE_TYPE_CHOICES = (
        (VALUE_TYPE_INTEGER, _("Whole number")),
        (VALUE_TYPE_FLOAT, _("Decimal number")),
        (VALUE_TYPE_BOOL, _("True/False")),
        (VALUE_TYPE_CHAR, _("String")),
        (VALUE_TYPE_CUSTOM, _("Custom")),
    )

    objects = ProjectSettingsQs.as_manager()

    value_validators = {
        VALUE_TYPE_INTEGER: lambda val: models.IntegerField().to_python(val),
        VALUE_TYPE_FLOAT: lambda val: models.FloatField().to_python(val),
        VALUE_TYPE_BOOL: lambda val: models.BooleanField().to_python(val),
        VALUE_TYPE_CHAR: lambda val: models.TextField().to_python(val),
        VALUE_TYPE_CUSTOM: lambda val: val,
    }

    @property
    def python_value(self):
        return self.value_validators[self.value_type](self.value)

    @property
    def python_pending_value(self):
        return self.value_validators[self.value_type](self.pending_value)

    def clean(self):
        validator = self.value_validators[self.value_type]
        try:
            validator(self.value)
        except ValidationError as ve:
            from rest_framework.serializers import ValidationError as DrfValidationError

            exc = DrfValidationError()
            setattr(exc, "detail", ErrorDetail(next(iter(list(ve.params.keys()))), ve.messages))
            setattr(exc, "model-validation", True)
            raise exc
        super().clean()

    name = models.CharField(max_length=80, null=False, blank=False, db_index=True, verbose_name=_("Name"))
    description = models.CharField(max_length=120, null=False, blank=False, verbose_name=_("Description"))
    value = models.CharField(max_length=320, null=False, blank=False, verbose_name=_("Value"))
    value_type = models.CharField(choices=VALUE_TYPE_CHOICES, null=False, blank=False, max_length=10)

    reserved = models.BooleanField(null=False, default=False)

    project = models.ForeignKey(
        swapper.get_model_name("django_project_base", "Project"), on_delete=models.CASCADE, null=False
    )

    pending_value = models.CharField(max_length=320, null=True, blank=True, verbose_name=_("Pending value"))
    action_required = models.BooleanField(default=False, null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        validator = self.value_validators[self.value_type]
        self.value = validator(self.value)
        if self.pending_value is not None:
            self.pending_value = validator(self.pending_value)
        if self.action_required:
            from django_project_base.base.event import ProjectSettingActionRequiredEvent

            ProjectSettingActionRequiredEvent(user=None).trigger(payload=self)
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        raise PermissionDenied

    class Meta:
        unique_together = [
            ["project", "name"],
        ]
        abstract = True


class ProjectSettings(BaseProjectSettings):
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "ProjectSettings")


@receiver(user_logged_in)
def user_logged_in(*args, **kwargs):
    from django_project_base.account.service.merge_users_service import MergeUsersService

    MergeUsersService().handle(**kwargs)


class BaseInvite(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, verbose_name=_("Id"))
    email = models.CharField(max_length=255, verbose_name=_("Email"))

    role = models.ForeignKey(
        swapper.get_model_name("django_project_base", "Role"), null=True, on_delete=models.SET_NULL
    )

    text = models.TextField(verbose_name=_("Invitation message"), null=True, blank=False)

    invited_by = models.ForeignKey(
        swapper.get_model_name("django_project_base", "Profile"),
        on_delete=models.CASCADE,
        related_name="project_user_invites",
    )
    accepted = models.DateTimeField(auto_now=False, null=True, blank=True)

    project = models.ForeignKey(
        swapper.get_model_name("django_project_base", "Project"), on_delete=models.CASCADE, null=False
    )

    class Meta:
        abstract = True
        unique_together = [
            ["project", "email"],
        ]


class Invite(BaseInvite):
    class Meta:
        swappable = swapper.swappable_setting("django_project_base", "Invite")
