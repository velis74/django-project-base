from typing import Optional

from django.conf import settings


def get_parameter(request, value_name: str, url_part: str) -> Optional[object]:
    value_from_header: Optional[int] = request.headers.get('Current-%s' % value_name.lower().title())
    if value_from_header is not None and value_from_header != '':
        return value_from_header
    try:
        project_info: Optional[str] = next(
            iter(filter(lambda f: f and url_part in f, request.path_info.split('/'))))
    except StopIteration:
        return None
    if project_info:
        return project_info[len(url_part):]
    return None


class UrlVarsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for value, config in settings.DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES.items():
            setattr(request, config['value_name'], get_parameter(request, value, config['url_part']))
        return self.get_response(request)
