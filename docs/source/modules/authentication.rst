Authentication
==============


***Impersonate user***

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


To increase AUTH performance you can set backend which caches users:
   - django_project_base.base.auth_backends.UsersCachingBackend
   - django_project_base.base.auth_backends.CachedTokenAuthentication


Example (add in settings.py):

.. code-block:: python

   # myproject/settings.py

   AUTHENTICATION_BACKENDS = (
       'django_project_base.base.auth_backends.UsersCachingBackend',  # cache users for auth to gain performance
       'django.contrib.auth.backends.ModelBackend',
   )

