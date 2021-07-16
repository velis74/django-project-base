from rest_framework import authentication


class SessionAuthentication(authentication.TokenAuthentication):
    def authenticate(self, request):
        user = getattr(request._request, 'user', None)

        if not user or not user.is_active:
            return None

        return (user, None)
