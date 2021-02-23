from typing import Optional

from django.conf import settings


def get_project(request) -> Optional[object]:
    project_header: Optional[int] = request.headers.get('Current-Project') or request.headers.get('current-project')
    if project_header is not None and project_header != '':
        return project_header
    project_url_part: str = settings.PROJECT_DEFINED_URL_PART
    try:
        project_info: Optional[str] = next(
            iter(filter(lambda f: f and project_url_part in f, request.path_info.split('/'))))
    except StopIteration:
        return None
    if project_info:
        return project_info[len(project_url_part):]
    return None


def get_language(request) -> Optional[object]:
    return None


class ProjectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_variables: dict = settings.BASE_REQUEST_URL_VARIABLES
        project: Optional[object] = get_project(request)
        language: Optional[object] = get_language(request)
        setattr(request, request_variables['project'], project)
        setattr(request, request_variables['language'], language)
        response = self.get_response(request)
        return response
