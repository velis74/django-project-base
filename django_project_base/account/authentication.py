from rest_framework.authentication import SessionAuthentication


# noinspection PyRedeclaration
class SessionAuthentication(SessionAuthentication):
    """
    This is needed because original SessionAuthentication doesn't return anything is authenticate_header. And this means
    that if user is not logged in, status of response would be 403 and not 401.
    If authenticate_header returns some string, status of response will be 401.

    This is only relevant for authentication class that if listed first in
    REST_FRAMEWORK / DEFAULT_AUTHENTICATION_CLASSES setting.
    Also see code in rest_framework.views.APIView.handle_exception and inside this function see call of function
    self.get_authenticate_header

    If you use this SessionAuthentication class instad of original one
    (rest_framework.authentication.SessionAuthentication) you must also set
    REST_REGISTRATION["LOGIN_AUTHENTICATE_SESSION"] to True in settings.py.
    Without it, user won't be logged in.
    See code in rest_registration.api.views.login.LoginView.post. Here is call to perform_login function. Inside that,
    there is call of should_authenticate_session() that returns True if there is original SessionAuthentication class
    listed in REST_FRAMEWORK / DEFAULT_AUTHENTICATION_CLASSES setting. If you are using inherited one,
    it will return False by default. Except you set REST_REGISTRATION["LOGIN_AUTHENTICATE_SESSION"] setting to True in
    settings.py.
    """

    def authenticate_header(self, request):
        return "sessionid"
