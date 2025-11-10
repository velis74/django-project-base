import copy

from gettext import gettext
from typing import Union

import swapper

from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.db.models import Model
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema, OpenApiResponse
from dynamicforms import fields
from dynamicforms.action import TableAction, TablePosition
from dynamicforms.mixins import DisplayMode
from dynamicforms.serializers import DynamicModelMixin, DynamicModelSerializerMixin, ModelSerializer
from dynamicforms.template_render.layout import Column, Layout, Row
from dynamicforms.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.response import Response

from django_project_base.account.middleware import ProjectNotSelectedError
from django_project_base.base.event import (
    ProjectSettingConfirmedEvent,
    ProjectSettingPendingResetEvent,
    SmsSenderChangedEvent,
)
from django_project_base.base.models import BaseProjectSettings
from django_project_base.base.permissions import CreateAny, is_staff, is_superuser, IsProjectOwnerOrReadOnly
from django_project_base.constants import EMAIL_SENDER_ID_SETTING_NAME, SMS_SENDER_ID_SETTING_NAME
from django_project_base.utils import get_pk_name


class ProjectSerializer(DynamicModelSerializerMixin, ModelSerializer):
    template_context = dict(url_reverse="project-base-project")
    form_titles = {"table": _("Projects"), "new": _("New project"), "edit": _("Edit project")}
    MODEL_FUNC_SETTING_NAME = "DJANGO_PROJECT_BASE_PROJECT_MODEL_AT_RUNTIME"
    LAYOUT_FUNC_SETTING_NAME = "DJANGO_PROJECT_BASE_PROJECT_LAYOUT_AT_RUNTIME"

    # logo = fields.FileField(display=DisplayMode.SUPPRESS, required=False)  # todo: not implemented UI

    class Meta:
        model = swapper.load_model("django_project_base", "Project")

        # we can remove the owner, because they're set at project creation and there will be a separate API for changing
        # TODO we currently don't support logos well. see DPB #3
        exclude = ("logo", "owner")

        layout = Layout(Row("name"), Row("slug"), Row("description"))


class ProjectViewSet(DynamicModelMixin, ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = (IsProjectOwnerOrReadOnly | CreateAny,)
    MODEL_FUNC_SETTING_NAME = "DJANGO_PROJECT_BASE_PROJECT_MODEL_AT_RUNTIME"

    @staticmethod
    def _get_queryset_for_request(request):
        model = DynamicModelMixin.determine_model_at_runtime_static(
            request, func_name=getattr(settings, ProjectViewSet.MODEL_FUNC_SETTING_NAME, None)
        )

        if not model:
            model = swapper.load_model("django_project_base", "Project")

        qs = model.objects
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

    def get_permissions(self):
        if self.action == "get_current_project":
            return [IsAuthenticated()]
        else:
            return super().get_permissions()

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
    )
    def get_current_project(self, request: Request, **kwargs) -> Response:
        try:
            instance = self.get_instance(request.selected_project.pk)
            serializer = self.get_serializer(instance)
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
    @get_current_project.mapping.put
    def update_current_profile(self, request: Request, **kwargs) -> Response:
        try:
            instance = self.get_instance(request.selected_project.pk, create_if_not_exists=True)
            serializer = self.get_serializer(instance, data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ProjectNotSelectedError as e:
            raise NotFound(e.message)

        return Response(serializer.data)

    def get_instance(self, pk, create_if_not_exists=False):
        model = self.get_queryset().model
        parent_model = list(model._meta.parents.keys())[0] if model._meta.parents else None

        try:
            return self.get_queryset().get(pk=pk)
        except model.DoesNotExist:
            if parent_model:
                try:
                    parent = parent_model.objects.get(pk=pk)
                    if create_if_not_exists:
                        instance: Model = model(**{f"{parent_model._meta.model_name}_ptr": parent})
                        instance.save_base(raw=True)
                        return instance
                    return parent
                except parent_model.DoesNotExist:
                    raise model.DoesNotExist()
            raise model.DoesNotExist()

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

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user
            if self.request and self.request.user and self.request.user.is_authenticated
            else None
        )

    def create(self, request, *args, **kwargs):
        create_response = super().create(request, *args, **kwargs)
        project = self.get_queryset().model.objects.get(slug=create_response.data["slug"])
        swapper.load_model("django_project_base", "ProjectMember").objects.create(project=project, member=request.user)
        project_settings_model = swapper.load_model("django_project_base", "ProjectSettings")
        project_settings_model.objects.create(
            name=EMAIL_SENDER_ID_SETTING_NAME,
            value=getattr(settings, "DEFAULT_EMAIL_SENDER_ID_SETTING_NAME", "") or gettext("Please enter value"),
            description=gettext("Email sender value for notifications"),
            value_type=BaseProjectSettings.VALUE_TYPE_CHAR,
            project=project,
            reserved=True,
        )
        project_settings_model.objects.create(
            name=SMS_SENDER_ID_SETTING_NAME,
            value=getattr(settings, "DEFAULT_SMS_SENDER_ID_SETTING_NAME", "") or gettext("Please enter value"),
            description=gettext("Sms sender value for notifications"),
            value_type=BaseProjectSettings.VALUE_TYPE_CHAR,
            project=project,
            reserved=True,
        )
        return create_response


class ProjectSettingsSerializer(ModelSerializer):
    template_context = dict(url_reverse="project-settings")

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        self.actions.actions = [a for a in self.actions.actions if a.name != "delete"]
        self.actions.actions.append(
            # TODO: https://taiga.velis.si/project/velis74-dynamic-forms/issue/837
            TableAction(
                position=TablePosition.FIELD_END,
                label="Reset pending",
                name="reset-pending",
                field_name="table_value",
                icon="ion-refresh-outline",
                display_style=dict(
                    asButton=False,
                    showIcon=True,
                    showLabel=False,
                ),
            ),
        )
        request = self.context.get("request")
        if request and (is_superuser(request.user) or is_staff(request.user)):
            # TODO: https://taiga.velis.si/project/velis74-dynamic-forms/issue/837
            self.actions.actions.append(
                TableAction(
                    position=TablePosition.ROW_END,
                    label="Confirm active",
                    name="confirm-setting-active",
                ),
            )

    id = fields.AutoGeneratedField(display=DisplayMode.HIDDEN)
    project = fields.PrimaryKeyRelatedField(
        display=DisplayMode.SUPPRESS, queryset=swapper.load_model("django_project_base", "Project").objects.all()
    )
    pending_value = fields.CharField(
        display=DisplayMode.SUPPRESS, required=False, allow_null=True, default=None, allow_blank=True
    )

    table_value = fields.CharField(
        source="value",
        display_table=DisplayMode.FULL,
        display_form=DisplayMode.SUPPRESS,
        label=gettext("Value"),
        read_only=True,
    )
    value = fields.CharField(
        display_table=DisplayMode.SUPPRESS,
        display_form=DisplayMode.FULL,
        required=True,
        allow_null=False,
        allow_blank=False,
    )

    def save(self, **kwargs):
        instance = copy.copy(self.instance)
        if instance:
            self.validated_data["pending_value"] = self.validated_data["value"]
            self.validated_data["value"] = instance.value

        if self.validated_data["value"] == self.validated_data["pending_value"]:
            self.validated_data["pending_value"] = None

        from django_project_base.base.event import EmailSenderChangedEvent

        EmailSenderChangedEvent(self.context["request"].user).trigger_changed(
            old_state=instance, new_state=self.Meta.model(**self.validated_data), payload=None
        )

        SmsSenderChangedEvent(self.context["request"].user).trigger_changed(
            old_state=instance, new_state=self.Meta.model(**self.validated_data), payload=None
        )
        saved = super().save(**kwargs)
        return saved

    def get_row_css_style(self, obj):
        if obj and obj.action_required:
            return "background-color:red;"
        return ""

    def to_representation(self, instance, row_data=None):
        representation = super().to_representation(instance, row_data)
        if instance and instance.pending_value is not None:
            representation["table_value"] = (
                f"{representation['value']} ({gettext('Pending')}: {instance.python_pending_value})"
            )
        return representation

    class Meta:
        model = swapper.load_model("django_project_base", "ProjectSettings")
        fields = (
            get_pk_name(model),
            "name",
            "table_value",
            "description",
            "value_type",
            "reserved",
            "value",
            "project",
            "pending_value",
        )
        layout = Layout(
            Row(Column("name")),
            Row(Column("value")),
            Row(Column("description")),
            Row(Column("value_type")),
            Row(Column("reserved")),
            size="large",
        )


class ProjectSettingsViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    # Pagination potrebujem, zato, da se sploh pokažejo zapisi v tabeli...
    #  Drugače funkcija replace_rows nič ne naradi
    #    - DF pričakuje da pride pagination like object (mora vsebovati "records", kjer so notri zapisi).
    #  Potrebujem pa vse postavke billinga, ker jih ob shranjevanju pošljem skupaj z glavo.
    pagination_class = ModelViewSet.generate_paged_loader(page_size=1000, ordering=["id"])

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
                # Swagger mock request pri inicializaciji swaggerja ne gre skozi middleware...
                # in zato request sploh nima selected_project attributa
                req.data["project"] = request.selected_project.pk if hasattr(request, "selected_project") else 0
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

    def filter_queryset_field(self, queryset, field, value):
        filter_field = "value" if field == "table_value" else field
        return super().filter_queryset_field(queryset, filter_field, value)

    def handle_create_validation_exception(self, e, request, *args, **kwargs):
        if getattr(e, "model-validation", False):
            raise ValidationError({e.detail: e.default_code})
        return super().handle_create_validation_exception(e, request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        list_response = super().list(request, *args, **kwargs)
        pending_settings = (
            self.get_queryset()
            .filter(pending_value__isnull=False)
            .exclude(pending_value="")
            .order_by(f"-{get_pk_name(self.get_serializer_class().Meta.model)}")
        )
        if pending_settings.exists():
            pk_name = get_pk_name(self.get_serializer_class().Meta.model)
            list_response.set_cookie(
                "setting-verification",
                f"{'*'.join(list(map(str, pending_settings.values_list(pk_name, flat=True))))}",
                expires=24 * 60 * 60,
                samesite="Lax",
            )
            return list_response
        list_response.delete_cookie("setting-verification")
        return list_response

    def _get_pk_from_request(self, request: Request) -> int:
        model = self.get_serializer_class().Meta.model
        pk_name = get_pk_name(model)
        pk = request.data.get(pk_name)
        if not pk:
            raise ValidationError({pk_name: [gettext("required")]})
        return pk

    @extend_schema(exclude=True)
    @transaction.atomic()
    @action(
        detail=False,
        methods=["POST"],
        url_name="confirm-setting",
        url_path="confirm-setting",
    )
    def confirm_pending_setting(self, request) -> Response:
        ProjectSettingConfirmedEvent(user=request.user).trigger(
            payload=get_object_or_404(self.get_serializer_class().Meta.model, pk=self._get_pk_from_request(request))
        )
        return Response()

    @extend_schema(exclude=True)
    @transaction.atomic()
    @action(
        detail=False,
        methods=["POST"],
        url_name="reset-pending",
        url_path="reset-pending",
    )
    def reset_pending_setting(self, request) -> Response:
        setting = get_object_or_404(self.get_serializer_class().Meta.model, pk=self._get_pk_from_request(request))
        if setting.pending_value is not None:
            ProjectSettingPendingResetEvent(user=request.user).trigger(payload=setting)
        return Response()

    @extend_schema(exclude=True)
    @transaction.atomic()
    @action(
        detail=False,
        methods=["POST"],
        url_name="confirm-setting-active",
        url_path="confirm-setting-active",
    )
    def confirm_setting_active(self, request) -> Response:
        if not (is_superuser(request.user) or is_staff(request.user)):
            raise PermissionDenied
        setting = get_object_or_404(self.get_serializer_class().Meta.model, pk=self._get_pk_from_request(request))
        call_command(
            "confirm_setting",
            setting.project.pk,
            setting.name,
        )
        return Response()
