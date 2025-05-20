import json

from typing import Iterable

import swapper

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from dynamicforms import fields, serializers, viewsets
from dynamicforms.action import Actions, FormButtonAction, FormButtonTypes
from dynamicforms.mixins import DisplayMode
from dynamicforms.template_render.layout import Layout, Row
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_registration.api.views import login

from django_project_base.account.social_auth.providers import get_social_providers, SocialProviderItem
from django_project_base.base.event import UserLoginEvent


class LoginSerializer(serializers.Serializer):
    form_titles = {"edit": _("Login")}
    actions = Actions(
        FormButtonAction(btn_type=FormButtonTypes.CANCEL, name="cancel", label=_("Back to site")),
        FormButtonAction(btn_type=FormButtonTypes.SUBMIT, name="submit", label=_("Login")),
        add_form_buttons=False,
    )

    template_context = dict(url_reverse="profile-base-login", url_reverse_kwargs=None)
    login = fields.CharField(label=_("Username"), required=True)
    password = fields.CharField(label=_("Password"), required=True, password_field=True)
    return_type = fields.ChoiceField(choices=["json", "cookie"], required=False, display_form=DisplayMode.HIDDEN)
    social_auth_providers = fields.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.update({"return-type": self.fields.pop("return_type")})

    def get_dialog_def(self):
        res = super().get_dialog_def()
        layout = Layout(Row("login", "password", "return-type", "social_auth_providers", "df_control_data"), columns=4)
        res["inline"] = layout.as_component_def(self)
        del res["inline"]["fields"]  # fields are already on this level
        return res

    def get_social_auth_providers(self, unused) -> Iterable[SocialProviderItem]:
        return map(lambda item: item._asdict(), get_social_providers())


@extend_schema_view(
    retrieve=extend_schema(
        description="Retrieves dialog definition for login dialog",
    ),
    create=extend_schema(
        description="<p>Logs in the user with given username and password. </p>"
        "<p>We support two methods of maintaining session information for your client: cookie-based and "
        "header-based.</p>"
        "<p>When you perform the account/login function, you can choose whether the function should return "
        'a session cookie or JSON with session id. Add parameter "return-type" with value "json" to login '
        'function parameters. This will return "sessionid" parameter in returned json instead of cookie. '
        "There is no CSRF when session is passed by the authorization header.</p>"
        "<p>If you choose the cookie, you will then need to supply the cookie(s) to all subsequent "
        "requests. Likewise, if you opt for session id as a variable, you will have to provide "
        "Authorization header to all subsequent requests.</p>"
        "<p>The default uses cookies as those also add a CSRF cookie providing a bit more security. "
        "Use of JSON / header should only be preferred for clients without support for cookies, such as "
        "background maintenance / data exchange scripts.</p>"
        "<p>When using the Authorisation header, use returned session api as token with token type "
        '"sessionid" and returned sessionid as credentials. Authorization: sessionid credentials</p>',
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="OK"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request. Missing either one of parameters or wrong login or password."
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Authentication credentials were not provided."),
        },
    ),
)
class LoginViewset(viewsets.SingleRecordViewSet):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def initialize_request(self, request, *args, **kwargs):
        # We need to lie to the CSRF middleware that CSRF processing is done, because otherwise CSRF middleware
        # (django/middleware/csrf.py -> process_view()) would execute request.POST, which would parse request data as
        # empty - because it is not encoded with form url encoding, but with JSON.
        #
        # As a result, DRF then doesn't get the JSON payload and can't process the request
        #
        # It is quite an ugly hack. But I cant find other way around. And security checks are anyway made by
        # rest_registration.api.views.
        request = super().initialize_request(request, *args, **kwargs)
        request.csrf_processing_done = True
        return request

    def new_object(self):
        return dict(login="", password="", return_type="cookie")

    def create(self, request: Request, *args, **kwargs) -> Response:
        # Tukaj ne smem narediti copy_request, ker se pri loginu nastavi kup nekih cookijev,
        # ki se potem ne pošljejo nazaj, ker se ne ohrani referenca na originalni request.
        req_data = json.loads(request._request.body.decode())

        if not req_data.get("password"):
            user = (
                swapper.load_model("django_project_base", "Profile")
                .objects.filter(username=request.data.get("login"))
                .first()
            )
            if user and user.is_new_user:
                from rest_framework import exceptions

                raise exceptions.PermissionDenied(detail="new_user")

        response = login(request._request)
        if response.renderer_context["request"].data.get("return-type", None) == "json":
            response.data.update({"sessionid": request.session.session_key})
            response.returntype = "json"
        if (
            response.status_code == status.HTTP_200_OK
            and (user_id := request.session.get("_auth_user_id"))
            and (user := get_user_model().objects.filter(pk=user_id).first())
        ):
            UserLoginEvent(user=user).trigger(payload=request)
        response.delete_cookie("register-flow")
        return response
