from typing import Union

import swapper
from django.conf import settings
from django.http import Http404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from dynamicforms import fields
from dynamicforms.mixins import DisplayMode
from dynamicforms.serializers import ModelSerializer
from dynamicforms.template_render.layout import Layout, Row
from dynamicforms.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.response import Response

from django_project_base.account.middleware import ProjectNotSelectedError
from django_project_base.base.models import BaseProjectSettings
from django_project_base.utils import get_pk_name


class ProjectSerializer(ModelSerializer):
    template_context = dict(url_reverse="project-base-project")

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)

        if self.context.get("view") and self.context["view"].format_kwarg == "componentdef":
            self.fields.fields["owner"].display_table = DisplayMode.SUPPRESS
            if self.context["view"].detail and self.instance.pk is None:
                # we are rendering new form
                self.fields.fields["owner"].display_form = DisplayMode.HIDDEN

    # logo = fields.FileField(display=DisplayMode.SUPPRESS, required=False)  # todo: not implemented UI
    owner = fields.AutoGeneratedField(display_table=DisplayMode.SUPPRESS, display_form=DisplayMode.HIDDEN)

    class Meta:
        model = swapper.load_model("django_project_base", "Project")
        exclude = ("logo",)  # TODO we currently don't support logos well. see DPB #3
        layout = Layout(Row("name"), Row("slug"), Row("description"))


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer

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

        return (owned_projects | member_projects).distinct()

    def get_queryset(self):
        return ProjectViewSet._get_queryset_for_request(self.request)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)

    @extend_schema(
        description="Get currently selected project",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    @action(
        methods=["GET"],
        detail=False,
        url_path="current",
        url_name="project-current",
        permission_classes=[IsAuthenticated],
    )
    def get_current_project(self, request: Request, **kwargs) -> Response:
        try:
            request.selected_project.get_deferred_fields()  # force immediate LazyObject evaluation
            serializer = self.get_serializer(request.selected_project)
        except ProjectNotSelectedError as e:
            raise NotFound(e.message)
        return Response(serializer.data)

    @extend_schema(
        description="Marks profile of calling user for deletion in future. Future date is determined " "by settings",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="No content"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    @get_current_project.mapping.post
    def update_current_profile(self, request: Request, **kwargs) -> Response:
        try:
            serializer = self.get_serializer(request.selected_project, data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ProjectNotSelectedError as e:
            raise NotFound(e.message)

        return Response(serializer.data)

    def get_object(self):
        SLUG_FIELD_NAME: str = settings.DJANGO_PROJECT_BASE_SLUG_FIELD_NAME

        lookup_field: str = self.lookup_field
        lookup_field_val: Union[str, int] = self.kwargs.get(self.lookup_field)

        proj_value_name = settings.DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES["project"]["value_name"]
        if getattr(self.request, proj_value_name, None) and lookup_field_val != "new":
            lookup_field_val = getattr(self.request, proj_value_name)

        def set_args(name: str) -> None:
            self.kwargs.pop(lookup_field, None)
            self.kwargs[name] = lookup_field_val
            self.lookup_field = name

        if lookup_field == "pk" or lookup_field == get_pk_name(self.get_queryset()):
            is_pk_auto_field: bool = self.get_queryset().model._meta.pk.get_internal_type() == "AutoField"
            try:
                int(lookup_field_val) if is_pk_auto_field and lookup_field_val else None
                return super().get_object()
            except (ValueError, Http404):
                set_args(SLUG_FIELD_NAME)
                return super().get_object()
        return super().get_object()

    def create(self, request, *args, **kwargs):
        create_response = super().create(request, *args, **kwargs)
        project = swapper.load_model("django_project_base", "Project").objects.get(slug=create_response.data["slug"])
        swapper.load_model("django_project_base", "ProjectMember").objects.create(project=project, member=request.user)
        return create_response


class ProjectSettingsSerializer(ModelSerializer):
    template_context = dict(url_reverse="project-settings")

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        self.actions.actions = [a for a in self.actions.actions if a.name != "delete"]

    project = fields.PrimaryKeyRelatedField(
        display=DisplayMode.SUPPRESS, queryset=swapper.load_model("django_project_base", "Project").objects.all()
    )

    def save(self, **kwargs):
        instance = self.instance
        saved = super().save(**kwargs)

        from django_project_base.base.event import EmailSenderChangedEvent

        EmailSenderChangedEvent(self.context["request"].user).trigger_changed(
            old_state=instance, new_state=saved, payload=None
        )

        return saved

    class Meta:
        model = swapper.load_model("django_project_base", "ProjectSettings")
        exclude = ()


class ProjectSettingsViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if (
            self.action == "retrieve" and self.detail is True and str(self.kwargs.get("pk", "")) != "new"
        ) or self.action in ("list", "update", "partial_update"):

            class AttrsReadOnlySer(ProjectSettingsSerializer):
                def __init__(self, *args, is_filter: bool = False, **kwds):
                    super().__init__(*args, is_filter=is_filter, **kwds)
                    if (
                        (view := kwds.get("context", {}).get("view"))
                        and view.detail is True
                        and str(view.kwargs.get("pk", "")) != "new"
                        and (sett := ProjectSettingsSerializer.Meta.model.objects.filter(pk=view.kwargs["pk"]).first())
                        and sett.reserved is True
                    ):
                        if view.action == "retrieve":
                            self.fields.fields["reserved"].read_only = True
                            self.fields.fields["name"].read_only = True
                            self.fields.fields["value_type"].read_only = True
                        else:
                            self.fields.fields["name"].required = False
                            self.fields.fields["value_type"].required = False

                def validate(self, attrs):
                    validated = super().validate(attrs)
                    if self.instance.reserved:
                        if "reserved" in validated and not validated["reserved"]:
                            raise PermissionDenied
                        if "name" in validated and validated["name"] != self.instance.name:
                            raise PermissionDenied
                        if "value_type" in validated and validated["value_type"] != self.instance.value_type:
                            raise PermissionDenied
                    return validated

                class Meta(ProjectSettingsSerializer.Meta):
                    pass

            return AttrsReadOnlySer

        return ProjectSettingsSerializer

    def initialize_request(self, request, *args, **kwargs):
        req = super().initialize_request(request, *args, **kwargs)
        if req.method.upper() not in SAFE_METHODS:
            try:
                req.data["project"] = self.request.selected_project.pk
            except ProjectNotSelectedError as e:
                raise NotFound(e.message)
        return req

    def get_queryset(self):
        try:
            return (
                self.get_serializer()
                .Meta.model.objects.filter(project__slug=self.request.selected_project.slug)
                .exclude(value_type=BaseProjectSettings.VALUE_TYPE_CUSTOM)
                .order_by("name")
            )
        except ProjectNotSelectedError:
            return self.get_serializer().Meta.model.objects.none()

    def handle_create_validation_exception(self, e, request, *args, **kwargs):
        if getattr(e, "model-validation", False):
            raise ValidationError({e.detail: e.default_code})
        return super().handle_create_validation_exception(e, request, *args, **kwargs)
