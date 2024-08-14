from typing import TYPE_CHECKING

import swapper

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from rest_framework.request import Request
from typing_extensions import Union

from django_project_base.project_selection_constants import SelectedProjectMode

if TYPE_CHECKING:
    from django_project_base.base.models import Project


def get_user_projects(user):
    """
    Returns queryset of all projects that user is permitted to
    """
    from django_project_base.base.models import get_project_model

    qs = get_project_model().objects
    # todo: request.user.is_authenticated this should be solved with permission class
    if not user or not user.is_authenticated:
        return qs.none()
    if user.is_superuser:
        return qs.all()
    user_profile = getattr(user, swapper.load_model("django_project_base", "Profile")._meta.model_name)
    # projects where current user is owner
    owned_projects = qs.filter(owner=user_profile)
    # projects where user is member
    member_projects = qs.filter(members__member=user_profile)

    return (owned_projects | member_projects).distinct()


def get_user_project(user) -> Union["Project", None]:
    """
    Returns project instance if user is permitted to exactly one project. Otherwise, returns None.
    """
    projects = list(get_user_projects(user)[:2])
    if len(projects) == 1:
        return projects[0]
    else:
        return None


def get_current_project_attr():
    """
    Returns key name for session, where slug of selected project will be stored
    """
    from django_project_base.constants import BASE_REQUEST_URL_VARIABLES_PROJECT_KEY

    return (
        getattr(settings, "DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES", {})
        .get(BASE_REQUEST_URL_VARIABLES_PROJECT_KEY, {})
        .get("value_name", "")
    )


def get_selected_project_mode():
    """
    Returns selected project mode from DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE setting.
    Default is SelectedProjectMode.FULL
    """
    return getattr(settings, "DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE", None) or SelectedProjectMode.FULL


class ProjectNotSelectedError(NotImplementedError):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)
        self.message = message


def selected_project_not_setup():
    """
    Error that is raised if project is not selected / defined
    """
    raise ProjectNotSelectedError(
        """The functionality called requires settings variables that establish currently selected project.
        Check docs for DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES and its "project" setting.
        The setting needs to be declared and currently selected project passed at least once from the front-end
        """
    )


def load_selected_project(slug: str):
    """
    Lazy project loader
    """

    def load():
        from django_project_base.base.models import get_project_model

        project_model = get_project_model()
        try:
            return project_model.objects.prefetch_related("owner").get(slug=slug)
        except project_model.DoesNotExist:
            selected_project_not_setup()

    return load


def get_project_from_request(request):
    """
    Returns project slug from request based on DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES setting
    """
    from django_project_base.constants import BASE_REQUEST_URL_VARIABLES_PROJECT_KEY

    request_url_settings = settings.DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES
    selected_project_slug = ""
    if isinstance(request_url_settings, dict) and BASE_REQUEST_URL_VARIABLES_PROJECT_KEY in request_url_settings:
        from django_project_base.base.middleware import get_parameter

        selected_project_slug = get_parameter(
            request,
            BASE_REQUEST_URL_VARIABLES_PROJECT_KEY,
            request_url_settings.get(BASE_REQUEST_URL_VARIABLES_PROJECT_KEY, {}).get("url_part", ""),
        )
    return selected_project_slug


def select_project(request: Request):
    """
    Select project by various means based on DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE setting
    - if set to FULL, user must select project in app
    - if set to AUTO, another middleware must set project_slug to request.
        Request attribute is the same as session key for storing slug
    - If set to PROMPT, project is only selected if user is permitted to exactly one project.
        Otherwise, project is not selected. If request needs project it must be selected other way, in other request
        parameters - data, queryset, etc...
    - If project slug is defined in DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE, then we just use that one
    """
    project_mode = get_selected_project_mode()
    current_project_attr = get_current_project_attr()
    project_slug = ""
    project = None
    if isinstance(project_mode, str):
        project_slug = project_mode
    elif project_mode == SelectedProjectMode.FULL:
        project_slug = get_project_from_request(request)
    elif project_mode == SelectedProjectMode.PROMPT:
        project = get_user_project(request.user)
        if project:
            project_slug = project.slug
    elif project_mode == SelectedProjectMode.AUTO:
        if current_project_attr:
            project_slug = getattr(request, current_project_attr, None)
    if project_slug:
        request.session[current_project_attr] = project_slug
    else:
        project_slug = request.session.get(current_project_attr, None)

    if project_slug:
        if project:
            return project
        return SimpleLazyObject(load_selected_project(project_slug))
    return SimpleLazyObject(selected_project_not_setup())


class SelectProjectMiddleware(MiddlewareMixin):
    """
    Middleware that sets selected project.
    It is mandatory for DPB to work correcty.

    If setting DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE is set to PROMPT this middleware must be executed after
    AuthenticationMiddleware (request must have user)
    """

    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        request.selected_project = select_project(request)
