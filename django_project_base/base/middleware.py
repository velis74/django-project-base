import threading
from typing import Optional

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest

_threadmap = {}


def has_current_request() -> bool:
    return threading.get_ident() in _threadmap


def get_current_request() -> WSGIRequest:
    return _threadmap[threading.get_ident()]


def get_parameter(request, value_name: str, url_part: str) -> Optional[object]:
    value_from_header: Optional[int] = request.headers.get(f"Current-{value_name.lower().title()}")
    if value_from_header is not None and value_from_header not in ("", "null"):
        return value_from_header

    path_parts = request.path_info.split("/")
    if isinstance(url_part, (list, tuple)) and isinstance(url_part[0], int) and isinstance(url_part[1], (list, tuple)):
        parm = path_parts[url_part[0]] if len(path_parts) > url_part[0] else None
        return parm if parm not in url_part[1] else None

    try:
        project_info = next(iter(filter(lambda f: f and url_part in f, path_parts)))
    except StopIteration:
        project_info = None
    if project_info:
        url_part_len = len(url_part)
        return project_info[url_part_len:]

    return None


class UrlVarsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for value, config in settings.DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES.items():
            if param := get_parameter(request, value, config["url_part"]):
                setattr(request, config["value_name"], param)

        _threadmap[threading.get_ident()] = request

        response = self.get_response(request)

        del _threadmap[threading.get_ident()]

        return response
