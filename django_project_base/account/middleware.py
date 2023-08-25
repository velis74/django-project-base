import json

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware as SessionMiddlewareBase
from rest_framework.authentication import get_authorization_header


class SessionMiddleware(SessionMiddlewareBase):
    def get_request_params(self, request):
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            body_data = json.loads(request.body.decode("utf-8"))
            if isinstance(body_data, list):
                return body_data[0]
            return body_data
        else:
            return getattr(request, request.method)

    def process_request(self, request):
        auth = get_authorization_header(request).split()
        if auth and auth[0].lower() == b"sessionid":
            session_key = auth[1].decode("utf-8")
            setattr(request, "_dont_enforce_csrf_checks", True)
        else:
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)

        request.session = self.SessionStore(session_key)
        current_project_attr = (
            getattr(settings, "DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES", {})
            .get("project", {})
            .get("value_name", None)
        )
        if current_project_attr and (curr_project_value := getattr(request, current_project_attr, None)):
            request.session[current_project_attr] = curr_project_value

    def process_response(self, request, response):
        if getattr(response, "returntype", None) == "json":
            process_response = super().process_response(request, response)
            process_response.cookies.pop("sessionid", None)
            process_response.cookies.pop("csrftoken", None)
            process_response.csrf_cookie_set = False

            return process_response

        return super().process_response(request, response)
