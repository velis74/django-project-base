Authentication
==============

Overridden rest_registration
----------------------------

If you want to use overrided rest_registration views, replace rest_registration urls with:

.. code-block:: python

  # myproject/urls.py
  from django_project_base.account import accounts_router

  urlpatterns = [
    path('account/', include(accounts_router.urls)),
    ...
  ]


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

To enable User caching backend to add the following line to *AUTHENTICATION_BACKENDS* section in settings.py:

.. code-block:: python

   # myproject/settings.py

   AUTHENTICATION_BACKENDS = (
       ...
       'django_project_base.base.auth_backends.UsersCachingBackend',  # cache users for auth to gain performance
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
  # If those users are logged in, they don't have permission until cache is cleared or they log out and log in again.
  UserProfile.objects.filter(username__in=['miha', 'janez']).update(is_superuser=True, is_staff=True)

  # After clearing users cache for those users will be able to work with additional permissions
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