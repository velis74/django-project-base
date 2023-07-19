import datetime

import django
import swapper
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.cache import cache
from django.db import transaction
from django.db.models import Case, CharField, ForeignKey, Model, QuerySet, Value, When
from django.db.models.functions import Coalesce, Concat
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from dynamicforms import fields
from dynamicforms.action import TableAction, TablePosition
from dynamicforms.mixins import DisplayMode
from dynamicforms.serializers import ModelSerializer
from dynamicforms.template_render.layout import Column, Layout, Row
from dynamicforms.template_render.responsive_table_layout import ResponsiveTableLayout, ResponsiveTableLayouts
from dynamicforms.viewsets import ModelViewSet
from rest_framework import exceptions, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.fields import IntegerField
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_registration.exceptions import UserNotFound

from django_project_base.account.constants import MERGE_USERS_QS_CK
from django_project_base.permissions import BasePermissions
from django_project_base.rest.project import ProjectSerializer
from django_project_base.settings import DELETE_PROFILE_TIMEDELTA, USER_CACHE_KEY


class ProfilePermissionsField(fields.ManyRelatedField):
    @staticmethod
    def to_dict(permission: Permission) -> dict:
        return {
            Permission._meta.pk.name: permission.pk,
            "codename": permission.codename,
            "name": permission.name,
        }

    def to_representation(self, value, row_data=None):
        if row_data and row_data.pk:
            return [ProfilePermissionsField.to_dict(p) for p in row_data.user_permissions.all()]
        return []


class ProfileGroupsField(fields.ManyRelatedField):
    def to_representation(self, value, row_data=None):
        if row_data and row_data.pk:
            return [
                {
                    Group._meta.pk.name: g.pk,
                    "permissions": [ProfilePermissionsField.to_dict(p) for p in g.permissions.all()],
                    "name": g.name,
                }
                for g in row_data.groups.all()
            ]
        return []


class ProfileSerializer(ModelSerializer):
    template_context = dict(url_reverse="profile-base-project")

    form_titles = {
        "table": "User profiles",
        "new": "New user",
        "edit": "Edit user",
    }

    id = fields.AutoGeneratedField(display=DisplayMode.HIDDEN)
    username = fields.AutoGeneratedField(display_table=DisplayMode.HIDDEN)
    first_name = fields.AutoGeneratedField(display_table=DisplayMode.HIDDEN)
    last_name = fields.AutoGeneratedField(display_table=DisplayMode.HIDDEN)
    bio = fields.AutoGeneratedField(display=DisplayMode.HIDDEN)  # read_only=True,
    theme = fields.AutoGeneratedField(display=DisplayMode.HIDDEN)  # read_only=True,
    password = fields.AutoGeneratedField(
        password_field=True, display=DisplayMode.HIDDEN, write_only=True, required=False
    )
    last_login = fields.AutoGeneratedField(display=DisplayMode.HIDDEN)  # read_only=True,
    date_joined = fields.AutoGeneratedField(display=DisplayMode.HIDDEN)  # read_only=True,
    is_active = fields.AutoGeneratedField(display=DisplayMode.HIDDEN)  # read_only=True,
    is_superuser = fields.AutoGeneratedField(display=DisplayMode.HIDDEN)  # read_only=True,
    is_staff = fields.AutoGeneratedField(display=DisplayMode.HIDDEN)  # read_only=True,
    avatar = fields.AutoGeneratedField(display_table=DisplayMode.HIDDEN)
    reverse_full_name_order = fields.AutoGeneratedField(display_table=DisplayMode.HIDDEN)

    full_name = fields.CharField(read_only=True, display_form=DisplayMode.HIDDEN)
    is_impersonated = fields.SerializerMethodField(display=DisplayMode.HIDDEN)
    password_invalid = fields.BooleanField(display_form=DisplayMode.HIDDEN, display_table=DisplayMode.HIDDEN)

    delete_at = fields.DateTimeField(read_only=True, display=DisplayMode.HIDDEN)
    permissions = ProfilePermissionsField(
        source="user_permissions",
        child_relation=fields.PrimaryKeyRelatedField(
            help_text=_("Specific permissions for this user"), queryset=Permission.objects.all(), required=False
        ),
        help_text=_("Specific permissions for this user"),
        required=False,
        allow_null=False,
        read_only=True,
        display=DisplayMode.HIDDEN,
    )

    groups = ProfileGroupsField(
        child_relation=fields.PrimaryKeyRelatedField(
            help_text=_(
                "The groups this user belongs to. A user will get all permissions granted to each of their groups."
            ),
            queryset=Group.objects.all(),
            required=False,
        ),
        help_text=_(
            "The groups this user belongs to. A user will get all permissions granted to each of their groups."
        ),
        required=False,
        allow_null=False,
        read_only=True,
        display=DisplayMode.HIDDEN,
    )

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        request = self._context["request"]

        if not request.user.is_superuser:
            self.fields.pop("is_staff", None)
            self.fields.pop("is_superuser", None)

        if self.instance and not isinstance(self.instance, (list, QuerySet)) and self.instance.pk != request.user.pk:
            # only show this field to the user for their account. admins don't see this field
            self.fields.pop("reverse_full_name_order", None)

        if request.user.is_superuser or request.user.is_staff:
            self.actions.actions.append(
                TableAction(
                    TablePosition.HEADER,
                    label=_("Export"),
                    title=_("Export"),
                    name="export",
                    icon="download-outline",
                )
            )
            if request.query_params.get("remove-merge-users", "false") in fields.BooleanField.TRUE_VALUES:
                self.actions.actions.append(
                    TableAction(
                        TablePosition.ROW_END,
                        label=_("Merge"),
                        title=_("Merge"),
                        name="add-to-merge",
                        icon="git-merge-outline",
                    ),
                )

    def get_is_impersonated(self, obj):
        try:
            request = self.context["request"]
            session = request.session
            return bool(session.get("hijack_history", [])) and obj.id == request.user.id
        except:
            pass
        return False

    class Meta:
        model = swapper.load_model("django_project_base", "Profile")
        exclude = ("user_permissions",)
        layout = Layout(
            Row(Column("username"), Column("password")),
            Row(Column("first_name"), Column("last_name")),
            # Row("reverse_full_name_order"),
            Row("email"),
            Row("phone_number"),
            Row("language"),
            Row("avatar"),
            columns=2,
            size="large",
        )
        responsive_columns = ResponsiveTableLayouts(
            auto_generate_single_row_layout=True,
            layouts=[
                ResponsiveTableLayout(auto_add_non_listed_columns=True),
                ResponsiveTableLayout("full_name", "email", auto_add_non_listed_columns=False),
            ],
        )


class ProfileRegisterSerializer(ProfileSerializer):
    password = fields.CharField(label=_("Password"), password_field=True)
    password_repeat = fields.CharField(label=_("Repeat Password"), password_field=True)

    class Meta(ProfileSerializer.Meta):
        layout = Layout(
            Row(Column("username")),
            Row(Column("first_name"), Column("last_name")),
            Row("password"),
            Row("password_repeat"),
            Row("email"),
            Row("phone_number"),
            Row("language"),
            columns=2,
            size="large",
        )
        exclude = ProfileSerializer.Meta.exclude + ("avatar",)

    def validate(self, attrs):
        super().validate(attrs)
        errors = {}
        password_repeat = attrs.pop("password_repeat")
        if not attrs["password"]:
            errors["password"] = _("Password is required")
        if not attrs["password"] == password_repeat:
            errors["password_repeat"] = _("Repeated value does not match inputted password")

        if not attrs["email"]:
            errors["email"] = _("Email is required")

        if errors:
            raise ValidationError(errors)
        return attrs


class MergeUserRequest(Serializer):
    user = IntegerField(min_value=1, required=True, allow_null=False)


class ProfileViewPermissions(BasePermissions):
    """
    Allows users to have full permissions on get/post (retrieving and adding new users).
    Other methods require authentication.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        if request.method == "GET" and request.path.split("/")[-1].split(".")[0] == "new":
            return True
        return super().has_permission(request, view)


@extend_schema_view(
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
)
class ProfileViewSet(ModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    permission_classes = (ProfileViewPermissions,)
    pagination_class = ModelViewSet.generate_paged_loader(30, ["un_sort", "id"])

    def get_queryset(self):
        qs = (
            swapper.load_model("django_project_base", "Profile")
            .objects.prefetch_related("projects", "groups", "user_permissions")
            .annotate(
                un=Concat(
                    Coalesce(
                        Case(When(first_name="", then="username"), default="first_name", output_field=CharField()),
                        Value(""),
                    ),
                    Value(" "),
                    Coalesce(
                        Case(When(last_name="", then="username"), default="last_name", output_field=CharField()),
                        "username",
                    ),
                ),
                un_sort=Concat(
                    Coalesce(
                        Case(When(last_name="", then="username"), default="last_name", output_field=CharField()),
                        "username",
                    ),
                    Value(" "),
                    Coalesce(
                        Case(When(first_name="", then="username"), default="first_name", output_field=CharField()),
                        Value(""),
                    ),
                ),
            )
        )

        qs = qs.exclude(delete_at__isnull=False, delete_at__lt=datetime.datetime.now())

        if getattr(self.request, "current_project_slug", None):
            # if current project was parsed from request, filter profiles to current project only
            qs = qs.filter(projects__project__slug=self.request.current_project_slug)
        elif not (self.request.user.is_staff or self.request.user.is_superuser):
            # but if user is not an admin, and the project is not known, only return this user's project
            qs = qs.filter(pk=self.request.user.pk)

        if self.request.query_params.get("remove-merge-users", "false") in fields.BooleanField.TRUE_VALUES:
            MergeUserGroup = swapper.load_model("django_project_base", "MergeUserGroup")
            exclude_qs = list(
                map(
                    str,
                    list(MergeUserGroup.objects.filter(created_by=self.request.user.pk).values_list("users", flat=True))
                    + cache.get(MERGE_USERS_QS_CK % self.request.user.pk, []),  # noqa: W503
                )
            )
            if exclude_qs:
                qs = qs.exclude(pk__in=map(int, ",".join(exclude_qs).split(",")))

        qs = qs.order_by("un", "id")
        return qs.distinct()

    def get_serializer_class(self):
        return ProfileSerializer

    def filter_queryset_field(self, queryset, field, value):
        if field == "full_name":
            return queryset.filter(un__icontains=value)
        return super().filter_queryset_field(queryset, field, value)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "search", description="Search users by all of those fields: username, email, first_name, last_name"
            )
        ],
        description="Get list of users",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK", response=get_serializer_class),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Default parameters for user registration",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="No content"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    @action(
        methods=["GET"],
        detail=False,
        url_path="register",
        url_name="profile-register",
        permission_classes=[],
    )
    def register_account(self, request: Request, **kwargs):
        serializer = ProfileRegisterSerializer(None, context=self.get_serializer_context())
        response_data: dict = serializer.data
        return Response(response_data)

    @extend_schema(
        description="Registering new account",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="No content"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    @register_account.mapping.post
    @transaction.atomic
    def create_new_account(self, request: Request, **kwargs):
        # set default values
        request.data["date_joined"] = datetime.datetime.now()
        request.data["is_active"] = True

        # call serializer to do the data processing drf way - hijack
        serializer = ProfileRegisterSerializer(
            None, context=self.get_serializer_context(), data=request.data, many=False
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(request.data["password"])
        user.save()
        return Response(serializer.validated_data)

    @extend_schema(
        description="Get user profile by id",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK", response=get_serializer_class),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Update profile data (partially)",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK", response=get_serializer_class),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Get user profile of calling user.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    @action(
        methods=["GET"],
        detail=False,
        url_path="current",
        url_name="profile-current",
        permission_classes=[IsAuthenticated],
    )
    def get_current_profile(self, request: Request, **kwargs) -> Response:
        user: Model = request.user
        serializer = self.get_serializer(user)
        response_data: dict = serializer.data
        if getattr(request, "GET", None) and request.GET.get("decorate", "") == "default-project":
            project_model: Model = swapper.load_model("django_project_base", "Project")
            response_data["default-project"] = None
            if project_model:
                ProjectSerializer.Meta.model = project_model
                response_data["default-project"] = ProjectSerializer(
                    project_model.objects.filter(owner=user).first()
                ).data
        return Response(response_data)

    @extend_schema(
        description="Marks profile of calling user for deletion in future. Future date is determined " "by settings",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="No content"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    @get_current_profile.mapping.post
    def update_current_profile(self, request: Request, **kwargs) -> Response:
        user: Model = request.user
        serializer = self.get_serializer(user, data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        description="Marks profile of calling user for deletion in future. Future date is determined " "by settings",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="No content"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    @get_current_profile.mapping.delete
    def mark_current_profile_delete(self, request: Request, **kwargs) -> Response:
        user: Model = getattr(request, "user", None)
        if not user:
            raise exceptions.AuthenticationFailed
        # user.is_active = False // user must still be able to login
        profile_obj = getattr(user, swapper.load_model("django_project_base", "Profile")._meta.model_name)
        profile_obj.delete_at = timezone.now() + datetime.timedelta(days=DELETE_PROFILE_TIMEDELTA)

        profile_obj.save(update_fields=["delete_at"])
        # user.save(update_fields=["is_active"])
        cache.delete(USER_CACHE_KEY.format(id=user.id))
        request.session.flush()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description="Immediately removes user from database",
        responses={
            status.HTTP_204_NO_CONTENT: OpenApiResponse(description="No content"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return super().destroy(request, *args, **kwargs)
        raise exceptions.PermissionDenied

    @extend_schema(exclude=True)
    @action(
        methods=["POST"],
        detail=False,
        url_path="merge-accounts",
        url_name="merge-accounts",
        permission_classes=[IsAuthenticated],
    )
    def merge_accounts(self, request, *args, **kwargs):
        from rest_registration.settings import registration_settings

        serializer = registration_settings.LOGIN_SERIALIZER_CLASS(data=request.data)
        serializer.is_valid(raise_exception=True)
        auth_user = self.request.user
        auth_user_is_main = str(self.request.data.get("account", "false")) in fields.BooleanField.TRUE_VALUES
        try:
            from django_project_base.account.service.merge_users_service import MergeUsersService

            user = registration_settings.LOGIN_AUTHENTICATOR(serializer.validated_data, serializer=serializer)
            MergeUserGroup = swapper.load_model("django_project_base", "MergeUserGroup")

            group, created = MergeUserGroup.objects.get_or_create(
                users=f"{auth_user.pk},{user.pk}", created_by=self.request.user.pk
            )
            MergeUsersService().handle(user=auth_user if auth_user_is_main else user, group=group)
            if not auth_user_is_main:
                # logout current user and redirect to login
                request.session.flush()
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except UserNotFound:
            raise UserNotFound
        except Exception:
            raise APIException

    @extend_schema(exclude=True)
    @action(
        methods=["POST"],
        detail=False,
        url_path="merge",
        url_name="merge",
        permission_classes=[IsAuthenticated, IsAdminUser],
    )
    def merge(self, request: Request, **kwargs) -> Response:
        ser = MergeUserRequest(data=request.data)
        ser.is_valid(raise_exception=True)
        ck = MERGE_USERS_QS_CK % self.request.user.pk
        ck_val = cache.get(ck, [])
        ck_val.append(ser.validated_data["user"])
        cache.set(ck, list(set(ck_val)), timeout=None)
        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(exclude=True)
    @action(
        methods=["POST"],
        detail=False,
        url_path="reset-user-data",
        url_name="reset-user-data",
        permission_classes=[IsAuthenticated],
    )
    @transaction.atomic()
    def reset_user_data(self, request: Request, **kwargs) -> Response:
        profile_model = swapper.load_model("django_project_base", "Profile")
        profile_obj = getattr(request.user, profile_model._meta.model_name)
        if request.data.get("reset"):
            base_user_models = (get_user_model(), profile_model)
            for mdl in django.apps.apps.get_models(include_auto_created=True, include_swapped=True):
                if mdl not in base_user_models and not mdl._meta.abstract and not mdl._meta.swapped:
                    for fld in [
                        f
                        for f in mdl._meta.fields
                        if isinstance(f, ForeignKey) and (f.related_model in base_user_models)
                    ]:
                        mdl.objects.filter(**{fld.attname: fld.to_python(profile_obj.pk)}).delete()
        profile_obj.delete_at = None
        profile_obj.save(update_fields=["delete_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
