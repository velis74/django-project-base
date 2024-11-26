from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware as SessionMiddlewareBase
from rest_framework.authentication import get_authorization_header


class SessionMiddleware(SessionMiddlewareBase):
    def process_request(self, request):
        auth = get_authorization_header(request).split()
        if auth and auth[0].lower() == b"sessionid":
            session_key = auth[1].decode("utf-8")
            setattr(request, "_dont_enforce_csrf_checks", True)
        else:
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)

        request.session = self.SessionStore(session_key)

    def process_response(self, request, response):
        if getattr(response, "returntype", None) == "json":
            process_response = super().process_response(request, response)
            process_response.cookies.pop("sessionid", None)
            process_response.cookies.pop("csrftoken", None)
            process_response.csrf_cookie_set = False

            return process_response

        return super().process_response(request, response)
