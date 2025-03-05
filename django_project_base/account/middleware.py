import json

import swapper

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware as SessionMiddlewareBase
from django.utils.functional import SimpleLazyObject
from rest_framework.authentication import get_authorization_header


class ProjectNotSelectedError(NotImplementedError):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)
        self.message = message


def selected_project_not_setup():
    raise ProjectNotSelectedError(
        """The functionality called requires settings variables that establish currently selected project.
        Check docs for DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES and its "project" setting.
        The setting needs to be declared and currently selected project passed at least once from the front-end
        """
    )


def load_selected_project(slug: str):
    def load():
        ProjectModel = swapper.load_model("django_project_base", "Project")
        try:
            return ProjectModel.objects.prefetch_related("owner").get(slug=slug)
        except ProjectModel.DoesNotExist:
            selected_project_not_setup()

    return load


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

        # determine if currently selected project has been passed with the request and set it to session if so
        # this requires UrlVarsMiddleware to have been installed before this middleware
        current_project_attr = (
            getattr(settings, "DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES", {})
            .get("project", {})
            .get("value_name", None)
        )

        # also set request.selected_project variables or throw errors on access if conditions not satisfied
        if current_project_attr:
            if curr_project_slug := getattr(request, current_project_attr, None):
                request.session[current_project_attr] = curr_project_slug
            else:
                curr_project_slug = request.session.get(current_project_attr, None)

            request.selected_project_slug = curr_project_slug
            request.selected_project = SimpleLazyObject(load_selected_project(curr_project_slug))
        else:
            request.selected_project_slug = SimpleLazyObject(selected_project_not_setup)
            request.selected_project = SimpleLazyObject(selected_project_not_setup)

    def process_response(self, request, response):
        process_response = super().process_response(request, response)
        if getattr(response, "returntype", None) == "json" or "/dynamicforms/progress" in request.path:
            # sometimes (i.e. at new user login) dynamicforms progress is called before user login...
            # and it can happen, that responses come back after login. But response have request session id,
            # that is not valid anymore (because login happened in the meantime).
            # And when such response come back to frontend it starts using this session data for further requests.
            # Which actually means that user is not logged in anymore.
            # So we can just remove session data from dynamicforms/progress response. It shouldn't be needed anyway.
            process_response.cookies.pop("sessionid", None)
            process_response.cookies.pop("csrftoken", None)
            process_response.csrf_cookie_set = False

        return process_response
