from typing import Any, cast, Dict, Optional, Union

import swapper

from django.core.validators import RegexValidator
from django.db.models import fields, Q, QuerySet
from django.utils.translation import gettext_lazy as _
from dynamicforms import fields as df_fields

from django_project_base.base.filter_to_model import filter_queryset_to_project


class HexColorField(fields.CharField):
    def __init__(self, *args, **kwargs):
        if "max_length" not in kwargs:
            kwargs["max_length"] = 7
        super().__init__(*args, **kwargs)
        self.validators.append(
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message=_("Value is not a hex color (e.g #88f or #8080ff)"),
            )
        )


class UserRelatedField(df_fields.PrimaryKeyRelatedField):
    def __init__(
        self,
        queryset_filter: Optional[Union[Q, Dict[str, Any]]] = None,
        queryset_exclude: Optional[Union[Q, Dict[str, Any]]] = None,
        **kwargs,
    ):
        kwargs["url_reverse"] = "profile-base-project-list"
        kwargs["query_field"] = "full_name"
        kwargs["additional_parameters"] = dict(select=1)
        kwargs["text_field"] = "full_name"
        kwargs["value_field"] = "id"
        super().__init__(**kwargs)
        self.queryset_filter = queryset_filter or {}
        self.queryset_exclude = queryset_exclude or {}
        self.filter_selected_project = True  # ImpersonateUserIdField overrides this (or any other; as needed)

    def get_queryset(self):
        # TODO This needs to be amended together with members editor such that it will be possible to specify
        #  in settings.py how to filter and sort project members
        qs = cast(QuerySet, swapper.load_model("django_project_base", "Profile").objects)

        if self.filter_selected_project:
            try:
                request = self.context.get("request", None)
                qs = filter_queryset_to_project(qs, "projects__project", request.selected_project)
            except AttributeError:
                # if the middleware setting current project is not even set (request.selected_project will except),
                #  we just show all users
                pass

        qs = qs.exclude(**self.queryset_exclude if isinstance(self.queryset_exclude, dict) else self.queryset_exclude)
        qs = qs.filter(**self.queryset_filter if isinstance(self.queryset_filter, dict) else self.queryset_filter)

        return qs.all()

    def display_value(self, instance):
        if not instance:
            return ""

        return str(instance)


class ProjectField(df_fields.PrimaryKeyRelatedField):
    # This class is used for fields that represents project fields.
    # There is serializer mixin ProjectMixin that shows or hides this field on form/table based on setting
    # DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE

    _attr_display_default = False
    _attr_queryset_default = False

    def __init__(self, **kw):
        from dynamicforms.mixins import DisplayMode

        from django_project_base.base.models import get_project_model

        if "display" not in kw:
            kw["display"] = DisplayMode.HIDDEN
            self._attr_display_default = True
        if "queryset" not in kw:
            kw["queryset"] = get_project_model().objects.none()
            self._attr_queryset_default = True

        super().__init__(**kw)

    def set_field_attrs(self, **kw):
        for k, v in kw.items():
            if getattr(self, f"_attr_{k}_default", True):
                setattr(self, k, v)
