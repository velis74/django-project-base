import re

from typing import Optional

import swapper

from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiTypes
from dynamicforms import fields as df_fields, serializers as df_serializers, viewsets as df_viewsets
from dynamicforms.action import Actions
from dynamicforms.mixins import DisplayMode
from rest_framework import fields, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_registration.api.views import change_password, logout, register
from rest_registration.settings import registration_settings
from social_django.models import UserSocialAuth

from django_project_base.account.rest.reset_password import ResetPasswordSerializer
from django_project_base.account.social_auth.providers import get_social_providers


def get_hijacker(request: Request) -> Optional:
    session = getattr(getattr(getattr(request, "_request", object()), "session", object()), "_session", dict())
    if (
        session.get("is_hijacked_user", False)
        and session.get("hijack_history", False)  # noqa: W503
        and request.user  # noqa: W503
        and request.user != AnonymousUser  # noqa: W503
    ):
        if user_pk := next(iter(session["hijack_history"]), None):
            if hijacker := get_user_model().objects.filter(pk=user_pk).first():
                return hijacker
    return None


class SocialAuthSerializer(ModelSerializer):
    class Meta:
        model = UserSocialAuth
        exclude = ("extra_data", "uid")


class SocialAuthProvidersViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == "social_auth_providers":
            return []
        elif self.action == "social_auth_providers_user":
            return [IsAuthenticated()]
        else:
            return super().get_permissions()

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
        }
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="social-auth-providers",
        url_name="social-auth-providers",
        authentication_classes=[],
    )
    def social_auth_providers(self, request: Request) -> Response:
        return Response(map(lambda item: item._asdict(), get_social_providers()))

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK", response=SocialAuthSerializer),
        }
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="social-auth-providers-user",
        url_name="social-auth-providers-user",
    )
    def social_auth_providers_user(self, request: Request) -> Response:
        return Response(SocialAuthSerializer(UserSocialAuth.objects.filter(user=self.request.user), many=True).data)


class LogoutSerializer(serializers.Serializer):
    revoke_token = fields.BooleanField(required=False)


class LogoutViewSet(viewsets.ViewSet):
    serializer_class = LogoutSerializer

    def get_permissions(self):
        if self.action == "logout":
            return [IsAuthenticated()]
        else:
            return super().get_permissions()

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        request._dont_enforce_csrf_checks = True
        return request

    @extend_schema(
        description="Logs out the user. Returns an error if the user is not authenticated. "
        "If revoke_token is provided, revokes the given token for a given user. If the token is not  "
        "provided, revoke all tokens for given user. ",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not authorised"),
        },
    )
    @action(detail=False, methods=["post"], url_name="logout")
    def logout(self, request: Request) -> Response:
        request._request._dont_enforce_csrf_checks = True
        return logout(request._request)


class ChangePasswordSerializer(df_serializers.Serializer):
    template_context = dict(
        url_reverse="change-password",
        dialog_classes="modal-lg",
        dialog_header_classes="bg-info",
    )
    form_titles = {
        "table": "",
        "new": _("Change password"),
        "edit": "",
    }

    invalid_password_notification = df_fields.SerializerMethodField(label="", display=DisplayMode.HIDDEN)
    old_password = df_fields.CharField(label=_("Current password"), required=True, password_field=True)
    password = df_fields.CharField(label=_("New password"), required=True, password_field=True)
    password_confirm = df_fields.CharField(label=_("Confirm new password"), required=True, password_field=True)

    actions = Actions(add_form_buttons=True)

    # noinspection PyMethodMayBeStatic
    def get_invalid_password_notification(self, obj):
        return _("Your password has expired. You must change it before continuing to use this application.")

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        view = kwds.get("context", {}).get("view")
        hijack_superuser = False
        if view and isinstance(view, ChangePasswordViewSet):
            hijack_superuser = view.is_hijacker_superuser()

        try:
            if kwds.get("context", {}).get("request").user.password_invalid and not hijack_superuser:
                self.fields["invalid_password_notification"].display = DisplayMode.FULL
        except:
            pass
        if hijack_superuser and "old_password" in self.fields:
            self.fields["old_password"].display = DisplayMode.HIDDEN


@extend_schema_view(
    retrieve=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH, enum=["new"])]),
)
class ChangePasswordViewSet(df_viewsets.SingleRecordViewSet):
    serializer_class = ChangePasswordSerializer
    permission_classes = [AllowAny]

    def is_hijacker_superuser(self):
        if hijacker := get_hijacker(self.request):
            return hijacker.is_superuser
        return False

    def get_serializer_class(self):
        ser = super().get_serializer_class()
        if self.is_hijacker_superuser():

            class SuperUserChangePasswordSerializer(ser):
                old_password = None

                def validate(self, attrs):
                    if attrs["password"] != attrs["password_confirm"]:
                        raise ValidationError({"password_confirm": _("Passwords do not match")})
                    return super().validate(attrs)

            return SuperUserChangePasswordSerializer
        return ser

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        # We need to set following flag (which is used while testing), because otherwise CSRF middleware
        # (django/middleware/csrf.py -> process_view()) would execute request.POST, which would cause
        # "django.http.request.RawPostDataException: You cannot access body after reading from request's data stream"
        # when request will be initialized and authenticated later for rest_registration.api.views.change_password
        #
        # It is quite an ugly hack. But I cant find other way around. And security checks are anyway made by
        # rest_registration.api.views.
        request._dont_enforce_csrf_checks = True
        return request

    def new_object(self):
        return dict(old_password="", password="", password_confirm="")

    @extend_schema(
        description="Change the user password.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    def create(self, request: Request) -> Response:
        def handle_password_changed(request):
            update_session_auth_hash(request, request.user)
            profile_obj = getattr(
                request.user,
                swapper.load_model("django_project_base", "Profile")._meta.model_name,
            )
            profile_obj.password_invalid = False
            profile_obj.save(update_fields=["password_invalid"])

        if self.is_hijacker_superuser():
            serializer = self.get_serializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            user = request.user
            user.set_password(serializer.validated_data["password"])
            user.save()
            handle_password_changed(request)
            return Response()

        response = change_password(request._request)
        if response.status_code == status.HTTP_200_OK:
            handle_password_changed(request)
        return response


class VerifyRegistrationViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action == "verify_registration":
            return []
        else:
            return super().get_permissions()

    @extend_schema(
        description="Verify registration with signature. The endpoint will generate an e-mail with a confirmation URL "
        "which the user should GET to confirm the account.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK", response=ResetPasswordSerializer),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Bad request"),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="verify-registration",
        url_name="verify-registration",
    )
    def verify_registration(self, request: Request) -> Response:
        if (
            (flow_id := request.COOKIES.get("register-flow"))
            and (code := cache.get(flow_id))
            and (req_code := request.data.get("code"))
            and code == req_code
            and len(code)
            and len(req_code)
            and (user := cache.get(code))
        ):
            user.is_active = True
            user.save(update_fields=["is_active"])
            login(request._request, user, backend="django_project_base.base.auth_backends.UsersCachingBackend")
            response = Response()
            response.delete_cookie("register-flow")
            return response
        raise ValidationError(dict(code=[_("Code invalid")]))

    @action(
        detail=False,
        methods=["post"],
        url_path="verify-registration-email-change",
        url_name="verify-registration-email-change",
    )
    def verify_registration_change_email(self, request: Request) -> Response:
        if (
            (flow_id := request.COOKIES.get("register-flow"))
            and (code := cache.get(flow_id))
            and len(code)
            and (user := cache.get(code))
        ):
            email = request.data.get("email")
            if not email:
                raise ValidationError(dict(email=[_("Email invalid")]))
            try:
                validate_email(email)
            except DjangoValidationError:
                raise ValidationError(dict(email=[_("Email invalid")]))
            user.email = email
            user.save(update_fields=["email"])
            if registration_settings.REGISTER_VERIFICATION_ENABLED:
                registration_settings.REGISTER_VERIFICATION_EMAIL_SENDER(request=request, user=user)
            return Response()
        raise PermissionDenied


class AbstractRegisterSerializer(df_serializers.Serializer):
    username = df_fields.CharField(required=True)
    email = df_fields.CharField(required=True)
    password = df_fields.CharField(required=True)
    password_confirm = df_fields.CharField(required=True)
    first_name = df_fields.CharField(required=False)
    last_name = df_fields.CharField(required=False)

    class Meta:
        abstract = True


class RegisterSerializer(AbstractRegisterSerializer):
    pass


class RegisterReturnSerializer(serializers.Serializer):
    id = fields.IntegerField()
    username = fields.CharField()
    email = fields.CharField()
    first_name = fields.CharField()
    last_name = fields.CharField()


@extend_schema(
    description="Register new user. The endpoint will generate an e-mail with a confirmation URL which the newly "
    "registered user should GET to activate the newly created account.",
    responses={
        status.HTTP_200_OK: OpenApiResponse(description="OK", response=RegisterReturnSerializer),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            description=re.sub(
                r" +",
                " ",
                """
                   There was a problem with the data. Response contains a JSON object showing validation errors per
                   field. JSON object keys are field names with issues, containing a list of issues and a
                   "non_field_errors" field containing errors that do not apply to a single field. Example: {
                     "password": [
                       "The password is too similar to the username.",
                       "This password is too short. It must contain at least 8 characters."
                     ],
                     "password_confirm": [
                       "Passwords do not match"
                     ],
                     "non_field_errors": []
                   }""".replace("\n", " "),
            )
        ),
    },
)
class RegisterViewSet(viewsets.ViewSet):
    serializer_class = RegisterSerializer

    @action(detail=False, methods=["post"], url_path="register", url_name="register")
    def register(self, request: Request) -> Response:
        return register(request._request)


class AdminAddUserSerializer(AbstractRegisterSerializer):
    template_context = dict(
        url_reverse="admin-add-user",
        dialog_classes="modal-lg",
        dialog_header_classes="bg-info",
    )
    form_titles = {
        "table": "",
        "new": _("Add new user"),
        "edit": "",
    }

    actions = Actions()


@extend_schema_view(
    retrieve=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH, enum=["new"])]),
)
class AdminAddUserViewSet(df_viewsets.SingleRecordViewSet):
    serializer_class = AdminAddUserSerializer

    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )  # TODO: permission should be based on project role

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        request.csrf_processing_done = True
        return request

    def new_object(self):
        return dict(
            username="",
            email="",
            password="",
            password_confirm="",
            first_name="",
            last_name="",
        )
