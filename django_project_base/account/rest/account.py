import re

import swapper
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiTypes
from dynamicforms import fields as df_fields, serializers as df_serializers, viewsets as df_viewsets
from dynamicforms.action import Actions
from rest_framework import fields, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_registration.api.views import (
    change_password, logout, register, reset_password, send_reset_password_link, verify_email, verify_registration
)

from django_project_base.account.social_auth.providers import get_social_providers


class SocialAuthProvidersViewSet(viewsets.ViewSet):
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
        permission_classes=[],
        authentication_classes=[],
    )
    def social_auth_providers(self, request: Request) -> Response:
        return Response(map(lambda item: item._asdict(), get_social_providers()))


class LogoutSerializer(serializers.Serializer):
    revoke_token = fields.BooleanField(required=False)


class LogoutViewSet(viewsets.ViewSet):
    serializer_class = LogoutSerializer

    @extend_schema(
        description="Logs out the user. Returns an error if the user is not authenticated. "
        "If revoke_token is provided, revokes the given token for a given user. If the token is not  "
        "provided, revoke all tokens for given user. ",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not authorised"),
        },
    )
    @action(detail=False, methods=["post"], url_name="logout", permission_classes=[IsAuthenticated])
    def logout(self, request: Request) -> Response:
        return logout(request._request)


class ChangePasswordSerializer(df_serializers.Serializer):
    template_context = dict(url_reverse="change-password", dialog_classes="modal-lg", dialog_header_classes="bg-info")
    form_titles = {
        "table": "",
        "new": _("Change password"),
        "edit": "",
    }

    old_password = df_fields.CharField(required=True, password_field=True)
    password = df_fields.CharField(required=True, password_field=True)
    password_confirm = df_fields.CharField(required=True, password_field=True)

    actions = Actions(add_form_buttons=True)


@extend_schema_view(
    retrieve=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH, enum=["new"])]),
)
class ChangePasswordViewSet(df_viewsets.SingleRecordViewSet):
    serializer_class = ChangePasswordSerializer

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
        response = change_password(request._request)
        if response.status_code == status.HTTP_200_OK:
            profile_obj = getattr(request.user, swapper.load_model("django_project_base", "Profile")._meta.model_name)
            profile_obj.password_invalid = False
            profile_obj.save(update_fields=["password_invalid"])
        return response


class ResetPasswordSerializer(serializers.Serializer):
    user_id = fields.CharField(required=True)
    timestamp = fields.CharField(required=True)
    signature = fields.CharField(required=True)
    password = fields.CharField(required=True)


class ResetPasswordViewSet(viewsets.ViewSet):
    serializer_class = ResetPasswordSerializer

    @extend_schema(
        description="Reset password through a link sent in email, given the signature and timestamp from the link.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK Reset link sent"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Bad request."),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Reset password verification disabled"),
        },
    )
    @action(detail=False, methods=["post"], url_path="reset-password", url_name="reset-password")
    def reset_password(self, request: Request) -> Response:
        return reset_password(request._request)

    @extend_schema(
        description="Verify email via signature.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK Email verified successfully"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Bad request"),
        },
    )
    @action(detail=False, methods=["post"], url_path="verify-email", url_name="verify-email")
    def verify_email(self, request: Request) -> Response:
        return verify_email(request._request)


class ResetPasswordAdminSerializer(df_serializers.Serializer):
    template_context = dict(
        url_reverse="admin-invalidate-password", dialog_classes="modal-lg", dialog_header_classes="bg-info"
    )
    form_titles = {
        "table": "",
        "new": _("Invalidate password"),
        "edit": "",
    }

    user_id = df_fields.IntegerField(required=True, help_text=_("Target user id"))

    actions = Actions()


@extend_schema_view(
    retrieve=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.STR, OpenApiParameter.PATH, enum=["new"])]),
)
class InvalidatePasswordAdminViewSet(df_viewsets.SingleRecordViewSet):
    serializer_class = ResetPasswordAdminSerializer

    permission_classes = (IsAuthenticated, IsAdminUser)  # TODO: permission should be based on project role

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        request._dont_enforce_csrf_checks = True
        return request

    def new_object(self):
        return dict(user_id="")

    @extend_schema(
        description="Marks the user password to be changed."
        "When user logs to an app UI user is shown change password dialog.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    def create(self, request: Request) -> Response:
        self.serializer_class(data=request.data).is_valid(raise_exception=True)
        profile_obj = get_object_or_404(
            swapper.load_model("django_project_base", "Profile"), user_ptr_id=request.data.get("user_id")
        )
        profile_obj.password_invalid = True
        profile_obj.save(update_fields=["password_invalid"])
        return Response()


class VerifyRegistrationSerializer(serializers.Serializer):
    user_id = fields.CharField(required=True)
    timestamp = fields.IntegerField(required=True)
    signature = fields.CharField(required=True)


class VerifyRegistrationViewSet(viewsets.ViewSet):
    serializer_class = VerifyRegistrationSerializer()

    @extend_schema(
        description="Verify registration with signature. The endpoint will generate an e-mail with a confirmation URL "
        "which the user should GET to confirm the account.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK", response=ResetPasswordSerializer),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Bad request"),
        },
    )
    @action(detail=False, methods=["post"], url_path="verify_registration", url_name="verify-registration")
    def verify_registration(self, request: Request) -> Response:
        return verify_registration(request._request)


class SendResetPasswordLinkSerializer(serializers.Serializer):
    login = fields.CharField(required=True)


class SendResetPasswordLinkViewSet(viewsets.ViewSet):
    serializer_class = SendResetPasswordLinkSerializer()

    @extend_schema(
        description="Send email with reset password link.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="OK Reset link sent", response=SendResetPasswordLinkSerializer()
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Bad request"),
            status.HTTP_404_NOT_FOUND: "Reset password verification disabled",
        },
    )
    @action(detail=False, methods=["post"], url_path="send-reset-password-link", url_name="send-reset-password-link")
    def send_reset_password_link(self, request: Request) -> Response:
        return send_reset_password_link(request._request)


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
                       "Passwords don't match"
                     ],
                     "non_field_errors": []
                   }""".replace(
                    "\n", " "
                ),
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
    template_context = dict(url_reverse="admin-add-user", dialog_classes="modal-lg", dialog_header_classes="bg-info")
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

    permission_classes = (IsAuthenticated, IsAdminUser)  # TODO: permission should be based on project role

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        request.csrf_processing_done = True
        return request

    def new_object(self):
        return dict(username="", email="", password="", password_confirm="", first_name="", last_name="")

    @extend_schema(
        description="Add new user.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not allowed"),
        },
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        from rest_registration.api.views.register import RegisterView

        view = RegisterView(request=request, serializer_class=self.serializer_class)
        response = view.post(request)
        if response.status_code == status.HTTP_201_CREATED:
            profile_obj = swapper.load_model("django_project_base", "Profile").objects.get(
                user_ptr_id=response.data[get_user_model()._meta.pk.name]
            )
            profile_obj.password_invalid = True
            profile_obj.save(update_fields=["password_invalid"])
        return response
