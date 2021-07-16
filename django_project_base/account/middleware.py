import json

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from rest_framework.authentication import get_authorization_header


class SessionMiddleware(SessionMiddleware):

    def get_request_params(self, request):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            body_data = json.loads(request.body.decode("utf-8"))
            if isinstance(body_data, list):
                return body_data[0]
            return body_data
        else:
            return getattr(request, request.method)

    def process_request(self, request):
        if self.get_request_params(request).get('return-type', None) == 'json':
            session_key = None
            auth = get_authorization_header(request).split()
            if auth and auth[0].lower() == b'sessionid':
                session_key = auth[1].decode("utf-8")
                setattr(request, '_dont_enforce_csrf_checks', True)
        else:
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)

        request.session = self.SessionStore(session_key)

    def process_response(self, request, response):
        if self.get_request_params(request).get('return-type', None) == 'json':
            auth = get_authorization_header(request).split()

            if not auth or auth[0].lower() != b'sessionid':
                return super(SessionMiddleware, self).process_response(request, response)
            else:
                process_response = super().process_response(request, response)
                process_response.cookies.pop('sessionid', None)
                process_response.cookies.pop('csrftoken', None)
                process_response.csrf_cookie_set = False

                return process_response

        return super(SessionMiddleware, self).process_response(request, response)
