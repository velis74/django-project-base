import threading

from typing import Optional

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest

_threadmap = {}
_threadmap_cnt = {}


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
        if request.path != "/favicon.ico":
            for value, config in settings.DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES.items():
                if param := get_parameter(request, value, config["url_part"]):
                    setattr(request, config["value_name"], param)

        threading_ident = threading.get_ident()
        # In some cases (e.g. wagtail draft document preview), there are multiple (two) runs through middlewares.
        # See wagtail/models/PreviewableMixin/make_preview_request.
        # We can't delete key from dict twice... so we introduce a counter, that will make sure,
        #   that key gets deleted only after we get response for the last time.
        _threadmap[threading_ident] = request
        _threadmap_cnt[threading_ident] = _threadmap_cnt.get(threading_ident, 0) + 1

        response = self.get_response(request)

        _threadmap_cnt[threading_ident] = _threadmap_cnt.get(threading_ident, 0) - 1
        if not _threadmap_cnt[threading_ident]:
            del _threadmap[threading_ident]
            del _threadmap_cnt[threading_ident]

        return response
