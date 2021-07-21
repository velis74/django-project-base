Authentication
==============

Obtaining and maintaining sessions
----------------------------------

We support two methods of maintaining session information for your client: cookie-based and header-based.

When you perform the account/login function, you can choose whether the function should return a session cookie or 
JSON with session id. Add parameter "return-type" with value "json" to login function parameters. This will return 
"sessionid" parameter in returned json instead of cookie. There is no CSRF when session is passed by the 
authorization header. See swagger documentation on login for further details.

If you choose the cookie, you will then need to supply the cookie(s) to all subsequent requests. Likewise, if you opt 
for session id as a variable, you will have to provide Authorization header to all subsequent requests.

The default uses cookies as those also add a CSRF cookie providing a bit more security. Use of JSON / header should
only be preferred for clients without support for cookies, such as background maintenance / data exchange scripts.

Our modified SessionMiddleware only overrides Django's as much to also accept the Authorization header and clears the 
session and CSRF cookies in the responses.

Activate project base accounts API endpoints
--------------------------------------------

.. code-block:: python

  # myproject/urls.py

  urlpatterns = [
    path('account/', include('django_project_base.account.urls')),
    ...
  ]

Session middleware
------------------

To enable project base's SessionMiddleware, replace Django contrib SessionMiddleware with project base's
SessionMiddleware in projects settings.py file. This is only necessary if you intend to support the JSON method for login
and keeping the session id.

.. code-block:: python

  # myproject/settings.py

  MIDDLEWARE = [
  ...
  'django_project_base.account.SessionMiddleware',
  ...]

Use of json session id in subsequent requests
---------------------------------------------

When using  the Authorisation header, use returned session api as token with token type "sessionid" and returned sessionid
as credentials.

.. code-block::

  Authorization: sessionid <credentials>

Impersonate user
----------------

Sometimes is useful if we can login into app as another user for debugging or help purposes.
User change is supported via REST api calls or you can use userProfile component (django_project_base/templates/user-profile/bootstrap/template.html)
which already integrates api functionality. Functionality is based on django-hijack package.

For determining which user can impersonate which user you can set your own logic. Example below:

.. code-block:: python

   # settings.py
    HIJACK_AUTHORIZATION_CHECK = 'app.utils.authorization_check'

   # app.utils.py
    def authorization_check(hijacker, hijacked):
        """
        Checks if a user is authorized to hijack another user
        """
        if my_condition:
            return True
        else:
            return False


User caching backend
--------------------

To increase AUTH performance you can set a backend that caches users.

To enable User caching backend replace django.contrib.auth.backends.ModelBackend with the following line to
*AUTHENTICATION_BACKENDS* section in settings.py:

.. code-block:: python

   # myproject/settings.py

   AUTHENTICATION_BACKENDS = (
       ...
       'django_project_base.base.auth_backends.UsersCachingBackend',
       ...
   )

User caching is not enabled for bulk updates by default, since Django doesn't call signal on .update() .bulk_update()
or .delete(). Updating data with a query or running bulk update, without clearing cache for every object could
potentially cause race conditions. Avoid it if possible, or take care of manually clearing the cache for the user.

Example for clearing cache after bulk update:

.. code-block:: python

  ...
  from django.core.cache import cache
  from django_project_base.settings import DJANGO_USER_CACHE
  ...
  # Bulk update multiple users. Give them superuser permission.
  # If those users are logged in, they don't have permission until cache is
  # cleared or they log out and log in again.
  UserProfile.objects.filter(username__in=['miha', 'janez']).update(
    is_superuser=True, is_staff=True)

  # After clearing users cache for those users will be able
  # to work with additional permissions
  staff = UserProfile.objects.filter(username__in=['miha', 'janez'])
        for user in staff:
            cache.delete(DJANGO_USER_CACHE % user.id)

It is possible to add a clear cache option also for bulk updates if needed with a custom QuerySet manager. You can find
example code below.

.. code-block:: python

  # models.py
  ...
  from django.core.cache import cache
  from django_project_base.settings import DJANGO_USER_CACHE
  ...
  class ProfilesQuerySet(models.QuerySet):
      def update(self, **kwargs):
          for profile in self:
              cache.delete(DJANGO_USER_CACHE % profile.id)
          res = super(ProfilesQuerySet, self).update(**kwargs)
          return res

      def delete(self):
        for profile in self:
            cache.delete(DJANGO_USER_CACHE % profile.id)
        res = super(ProfilesQuerySet, self).delete()
        return res


  class UserProfile(BaseProfile):
      """Use this only for enabling cache clear for bulk update"""
      objects = ProfilesQuerySet.as_manager()
  ...

Social auth integrations
------------------------

Django Project Base offers easy-to-setup social authentication mechanism. Currently the following providers are
supported:

 - Facebook
    - provider identifier: facebook
 - Google
    - provider identifier: google-oauth2
 - Twitter
    - provider identifier: twitter
 - Microsoft
    - provider identifier: microsoft-graph
 - Github
    - provider identifier: github
 - Gitlab
    - provider identifier: gitlab

OAuth providers require redirect URL which is called after the authentication process in Oauth flow.

Your redirect url is: [SCHEME]://[HOST]/account/social/complete/[PROVIDER IDENTIFIER]/

Information which settings are required for a social provider can be
found at https://python-social-auth.readthedocs.io/en/latest/backends/index.html

For social authentication functionalities `Python Social Auth <https://python-social-auth.readthedocs.io>`_ library
was used. Please checkout this documentation to make any custom changes.


**Installation**

 Add app to your installed apps.

 .. code-block:: python

    # myproject/settings.py

    from django_project_base.accounts import ACCOUNT_APP_ID

    INSTALLED_APPS = [
        ...
        'social_django',
        ACCOUNT_APP_ID,
        ...
     ]


 Make sure you have django project base urls included:

 .. code-block:: python

    # url.py

    urlpatterns = [
      .....
      path('account/', include(accounts_router.urls)),
      path('account/social/', include('social_django.urls', namespace="social")),
      .....
   ]


 Run migrations:

 .. code-block:: python

    python manage.py migrate


**Social login integration example - Google**

To enable a social provider create an account at provider webpage and create an oauth app. For example for Google OAuth
login visit https://console.developers.google.com/apis/credentials. Click + CREATE CREDENTIALS and select
Oauth Client ID. Then create OAuth app with OAuth Consent screen.

Example value for Authorized JavaScript origins can be http://localhost:8080.

Example value for Authorized redirect URIs can be http://localhost:8080/account/social/complete/google-oauth2/.

To enable Google OAuth login add folowing to settings:

 .. code-block:: python

    # myproject/settings.py
    # enable google social login
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '*Client ID*'
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '*Client secret*'
