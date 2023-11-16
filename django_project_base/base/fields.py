import swapper
from django.core.validators import RegexValidator
from django.db.models import fields
from django.utils.translation import gettext_lazy as _
from dynamicforms import fields as df_fields

from django_project_base.base.middleware import get_current_request


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
    def __init__(self, **kwargs):
        kwargs["url_reverse"] = "profile-base-project-list"
        kwargs["query_field"] = "full_name"
        kwargs["additional_parameters"] = dict(select=1)
        kwargs["text_field"] = "full_name"
        kwargs["value_field"] = "id"
        super().__init__(**kwargs)

    def get_queryset(self):
        # TODO This needs to be amended together with members editor such that it will be possible to specify
        #  in settings.py how to filter and sort project members
        qs = swapper.load_model("django_project_base", "Profile").objects
        request = get_current_request()
        if request and getattr(request, "selected_project_slug", None):
            # if current project was parsed from request, filter profiles to current project only
            qs = qs.filter(projects__project__slug=request.selected_project_slug)
        return qs.all().distinct()

    def display_value(self, instance):
        if not instance:
            return ""

        return instance.get_full_name()
