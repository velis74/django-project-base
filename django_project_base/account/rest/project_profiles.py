import json
import re

from io import BytesIO

import pandas as pd
import swapper

from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from dynamicforms import fields, serializers
from dynamicforms.action import TableAction, TablePosition
from dynamicforms.viewsets import SingleRecordViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.utils import model_meta

from django_project_base.account.rest.profile import ProfileSerializer, ProfileViewSet

from ...base.permissions import is_project_owner, is_superuser, IsProjectOwnerOrMemberReadOnly, project_is_selected
from ..middleware import ProjectNotSelectedError
from .project_profiles_utils import filter_project_members_fields, get_project_members


class ProjectProfilesSerializer(ProfileSerializer):
    template_context = dict(url_reverse="profiles")

    def __init__(self, *args, **kwargs):
        request = kwargs["context"]["request"]
        self.member_fields_read_only = bool(re.findall(r"profile/current", request.path))

        user = request.user
        project = request.selected_project

        self.user_is_admin = is_superuser(user) or (project_is_selected(project) and is_project_owner(user, project))
        self.user_is_me = (
            len(args) == 1
            and isinstance(args[0], swapper.load_model("django_project_base", "Profile"))
            and user.id == args[0].id
        )

        super().__init__(*args, **kwargs)

        if self.user_is_admin:
            self.actions.actions.extend(
                [
                    TableAction(
                        TablePosition.ROW_END,
                        label=_("Reset password"),
                        name="reset-password",
                        icon="ion-refresh-outline",
                    ),
                    TableAction(
                        TablePosition.ROW_END,
                        label=_("Merge"),
                        name="add-to-merge",
                        icon="ion-git-merge-outline",
                    ),
                ]
            )

    def get_fields(self):
        ProjectMember = swapper.load_model("django_project_base", "ProjectMember")
        info = model_meta.get_field_info(ProjectMember)
        for field in ProjectMember().project_members_fields:
            source = f"first_project.{field.name}"
            extra_kwargs = dict(source=source, required=False, read_only=self.member_fields_read_only)
            field_class, field_kwargs = self.build_field(field.name, info, ProjectMember, source)
            field_kwargs = self.include_extra_kwargs(field_kwargs, extra_kwargs)
            self._declared_fields[field.name] = field_class(**field_kwargs)
        res = super().get_fields()

        if not self.user_is_admin and not self.user_is_me:
            # if user is not super admin make all fields readonly
            for field in res.values():
                if getattr(field, "read_only", None) is not None:
                    setattr(field, "read_only", True)

        if self.user_is_admin:
            password_field = res.get("password", None)
            if password_field:
                setattr(password_field, "display", fields.DisplayMode.FULL)
                setattr(password_field, "display_table", fields.DisplayMode.HIDDEN)

        return res

    def translate_relation_fields(self, field_name: str) -> str:
        ProjectMember = swapper.load_model("django_project_base", "ProjectMember")
        if field_name in ProjectMember().project_members_fields_names:
            return f"projects__{field_name}"
        else:
            return field_name

    def get_visible_fields(self):
        return [(name, field) for (name, field) in self.fields.items() if field.display == fields.DisplayMode.FULL]


class ProjectProfilesViewSet(ProfileViewSet):
    serializer_class = ProjectProfilesSerializer
    # see special case in the permission class if you need to change the permission class
    permission_classes = (IsProjectOwnerOrMemberReadOnly,)

    def get_serializer_class(self):
        return ProjectProfilesSerializer

    def filter_queryset_field(self, queryset, field, value):
        if field == "state" and value:
            return queryset.alias(member_state=F("projects__state")).filter(member_state=value)
        return super().filter_queryset_field(queryset, field, value)

    def save_club_member_data(self, request: Request, user, **kwargs):
        if user is None:
            return
        project = request.selected_project

        club_member = None
        ProjectMember = swapper.load_model("django_project_base", "ProjectMember")

        if project:
            club_member = ProjectMember.objects.filter(member=user).filter(project=project).first()

        # if club member data cant be retrieved, we can't save anything
        if club_member:
            for name, value in kwargs.items():
                setattr(club_member, name, value)
            club_member.save()

    @transaction.atomic
    def create(self, request: Request, *args, **kwargs) -> Response:
        ProjectMember = swapper.load_model("django_project_base", "ProjectMember")
        Profile = swapper.load_model("django_project_base", "Profile")
        data = {
            name: request.data.pop(name, None)
            for name in ProjectMember().project_members_fields_names
            if name in request.data
        }
        # hash password if it exists
        if "password" in request.data:
            request.data["password"] = make_password(request.data["password"])
        response = super().create(request, *args, **kwargs)
        user = Profile.objects.get(pk=response.data["id"])
        try:
            ProjectMember.objects.create(project=request.selected_project, member=user)
        except ProjectNotSelectedError as e:
            raise PermissionDenied(e.message)

        self.save_club_member_data(request, user, **data)
        return response

    @transaction.atomic
    def update(self, request: Request, *args, **kwargs) -> Response:
        ProjectMember = swapper.load_model("django_project_base", "ProjectMember")
        data = {
            name: request.data.pop(name, None)
            for name in ProjectMember().project_members_fields_names
            if name in request.data
        }
        self.save_club_member_data(request, self.get_object(), **data)
        # hash password if it exists
        if "password" in request.data:
            request.data["password"] = make_password(request.data["password"])
        return super().update(request, *args, **kwargs)


class ProfileExportSerializer(serializers.Serializer):
    template_context = dict(url_reverse="profiles-export")

    form_titles = {
        "table": "",
        "new": _("Export users"),
        "edit": "",
    }

    template = fields.ChoiceField(
        label=_("Template"),
        choices=(
            # (1, _("PDF")),
            (2, _("CSV")),
            (3, _("XLS")),
        ),
    )

    profile_fields = fields.MultipleChoiceField(label=_("Profile Fields"), allow_null=True)

    filter_data = fields.JSONField(display=fields.DisplayMode.HIDDEN)

    print_filter = fields.BooleanField(label=_("Print Filter"), default=False)

    def __init__(self, *args, **kwargs):
        profile_serializer = ProjectProfilesSerializer(None, **kwargs)
        visible_profile_fields = [(name, field.label) for name, field in profile_serializer.get_visible_fields()]
        super().__init__(*args, **kwargs)
        self.fields["profile_fields"].choices = visible_profile_fields


class ProfileExportViewSet(SingleRecordViewSet):
    serializer_class = ProfileExportSerializer

    def get_permissions(self):
        if self.action == "download":
            return [IsAuthenticated()]
        else:
            return super().get_permissions()

    def new_object(self):
        filter_data = self.request.query_params.get("filter_data", None)
        if filter_data:
            filter_data = json.loads(filter_data)
        return dict(template=None, profile_fields=None, print_filter=True, filter_data=filter_data)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)  # type: ProfileExportSerializer
        ser.is_valid(raise_exception=True)

        filter_data = ser.data.get("filter_data", None)
        print_filter = ser.data.get("print_filter", False)

        file_name = "members"

        if filter_data:
            active_filters = {name: value for name, value in filter_data.items() if value is not None}
            if print_filter and len(active_filters) in [1, 2]:
                file_name += "-" + ",".join(["-".join([name, str(value)]) for name, value in active_filters.items()])

        data = dict(ser.data)
        data["file_name"] = file_name

        return Response(data)

    @action(methods=["POST"], detail=False, url_path="download", url_name="profile-export-download")
    def download(self, request: Request, **kwargs):
        profile_serializer = ProjectProfilesSerializer(None, context=self.get_serializer_context(), data=request.data)
        visible_profile_fields = {
            name: profile_serializer.translate_relation_fields(name)
            for name, _ in profile_serializer.get_visible_fields()
        }
        column_names = {
            visible_profile_fields[name]: field.label for name, field in profile_serializer.get_visible_fields()
        }

        ser = self.get_serializer(data=request.data)  # type: ProfileExportSerializer
        ser.is_valid(raise_exception=True)

        profile_fields = ser.data.get("profile_fields", None)
        template = ser.data.get("template", None)
        filter_data = ser.data.get("filter_data", None)
        file_name = ser.data.get("file_name", "members")

        profile_items_q = get_project_members(self.request)

        if filter_data:
            for field_name, value in filter_data.items():
                profile_items_q = filter_project_members_fields(profile_items_q, field_name, value)

        selected_fields = (
            [name for name in visible_profile_fields.values()]
            if profile_fields is None
            else [visible_profile_fields[field] for field in profile_fields if field in visible_profile_fields]
        )

        profile_items_q = profile_items_q.values(*selected_fields)

        output = BytesIO()
        df = pd.DataFrame(profile_items_q, columns=list(selected_fields))
        df.rename(columns=column_names, inplace=True)

        if template == 2:
            df.to_csv(output)
            output.seek(0)
            response = HttpResponse(output, content_type="text/csv")
            response["Content-Disposition"] = f'attachment; filename="{file_name}.csv"'
            response["Content-Name"] = f"{file_name}.csv"
            return response
        elif template == 3:
            df.to_excel(output)
            output.seek(0)
            response = HttpResponse(output, content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = f'attachment; filename="{file_name}.xlsx"'
            response["Content-Name"] = f"{file_name}.xlsx"
            return response
        else:
            raise NotFound(f"Export template {template} not found")
