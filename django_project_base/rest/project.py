from typing import Union

import swapper
from django.conf import settings
from django.http import Http404
from dynamicforms import fields
from dynamicforms.mixins import DisplayMode
from dynamicforms.serializers import ModelSerializer
from dynamicforms.viewsets import ModelViewSet

from django_project_base.base.middleware import get_parameter


class ProjectSerializer(ModelSerializer):
    template_context = dict(url_reverse="project-base-project")

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)

        if self.context.get("view") and self.context["view"].format_kwarg == "componentdef":
            self.fields.fields["owner"].display_table = DisplayMode.SUPPRESS
            if self.context["view"].detail and self.instance.pk is None:
                # we are rendering new form
                self.fields.fields["owner"].display_form = DisplayMode.HIDDEN

    logo = fields.FileField(display=DisplayMode.SUPPRESS, required=False)  # todo: not implemented UI

    class Meta:
        model = swapper.load_model("django_project_base", "Project")
        exclude = ()


class ProjectViewSet(ModelViewSet):
    def new_object(self: ModelViewSet):
        new_object = super().new_object()
        if self.request and self.request.user and self.request.user.is_authenticated:
            new_object.owner = getattr(
                self.request.user, swapper.load_model("django_project_base", "Profile")._meta.model_name
            )

        return new_object

    @staticmethod
    def _get_queryset_for_request(request):
        qs = swapper.load_model("django_project_base", "Project").objects
        # todo: request.user.is_authenticated this should be solved with permission class
        if not request or not request.user or not request.user.is_authenticated:
            return qs.none()
        user_profile = getattr(request.user, swapper.load_model("django_project_base", "Profile")._meta.model_name)
        # projects where current user is owner
        owned_projects = qs.filter(owner=user_profile)
        # projects where user is member
        member_projects = qs.filter(members__member=user_profile)
        # TODO: USE FILTER owned_projects AND member_projects
        queryset = (owned_projects | member_projects).distinct()

        return queryset.all()

    def get_queryset(self):
        return ProjectViewSet._get_queryset_for_request(self.request)

    def get_serializer_class(self):
        return ProjectSerializer

    def get_object(self):
        SLUG_FIELD_NAME: str = settings.DJANGO_PROJECT_BASE_SLUG_FIELD_NAME

        lookup_field: str = self.lookup_field
        lookup_field_val: Union[str, int] = self.kwargs.get(self.lookup_field)

        if (
            value := getattr(settings, "DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES", {})
            .get("project", {})
            .get("url_part", "project-")
        ):
            if param := get_parameter(self.request, "project", value) and lookup_field_val != "new":
                lookup_field_val = param

        def set_args(name: str) -> None:
            self.kwargs.pop(lookup_field, None)
            self.kwargs[name] = lookup_field_val
            self.lookup_field = name

        if lookup_field == "pk" or lookup_field == self.get_queryset().model._meta.pk.name:
            is_pk_auto_field: bool = self.get_queryset().model._meta.pk.get_internal_type() == "AutoField"
            try:
                int(lookup_field_val) if is_pk_auto_field and lookup_field_val else None
                return super().get_object()
            except (ValueError, Http404):
                set_args(SLUG_FIELD_NAME)
                return super().get_object()
        return super().get_object()
