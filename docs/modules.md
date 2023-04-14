# Modules


## Project


Project API is core part of Django project base.

### Project slug

DJANGO_PROJECT_BASE_SLUG_FIELD_NAME

When creating models with slug field they should be named with this setting value. This enables that we can use object
slug instead of object pk when making api requests. Default value is "slug".

### DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES

```python

    DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES: {
        'project': {'value_name': 'current_project_slug', 'url_part': 'project-'},
        'language': {'value_name': 'current_language', 'url_part': 'language-'}
    }
```

This setting defines a dictionary of attribute names on the request object. E.g. project info is set on the request
object under property current_project_slug. Language information is set on request objects under property current
language. Is language or project is given in request path like language-EN, then url_part settings is found and EN
string is taken as language value.


# Profile

Account / profile API.

Django project base uses multi-table inheritance together with abstract base classes to provide boilerplate user
profile fields. The goal of our profile was to provide some social aspects as well as cover small communities where
personal details like phone numbers are more commonly used as means of communication. Of course, any of the fields may
be freely skipped with customisation.

### Profile reverse name order

Settings option **PROFILE_REVERSE_FULL_NAME_ORDER** defines first_name, last_name order for readonly field *full_name*.
Default order is *False* - "First Last". Changing setting to true will reverse order to "Last First".

Global setting can be also overrided with profile option reverse_full_name_order (bool).

### Deleting profile

Super admins can either delete profile or mark it for deletion in future.

User cannot delete their profile, they can only mark it for deletion in future. After confirmation for deletion, their
profile is marked for deletion, user is logged out and is not able to log in or use features that require logged in
user.

Settings value **DELETE_PROFILE_TIMEDELTA** defines how far in future user profile will be actually deleted with
automatic process. Value is set in days. The intent is in keeping user data in case they change their mind and
re-register.

### Existing profile table troubleshooting

You may find yourself in a pinch if your project already has a user profile table and it's not linked to
django.auth.User model using multi-model inheritance. Instead, you might have implemented it with a separate
OneToOneField or even a ForeignKey. Even worse, if you linked all the user fields to this model and not the
django.auth.User model.

You are SOL: migration will not be a matter of extending the model, but rather one of REPLACING the model. It is,
however, only a 4-step (optionally 5-step) process in terms of migrations:

1. Declare the new user profile model, new foreign keys to the profile model in all tables where you link to your
   existing model. Basically you have duplicated all the fields and the model. run `makemigrations`.
2. Create a new `runPython` migration where you copy all the values from existing fields to new fields. This cannot
   be done in the first migration, you will just get `an error <https://stackoverflow.com/questions/12838111>`_
   running it.

   a. if your references to previous profile model were to its own ID and not to django.auth.User model ID, you will
      have to also perform the translations between the two ID fields. Should be relatively easy in you migration code,
      something like:

```python
# assumes you had a relation named "user" in your profile table
model.objects.update(**{
    field_name + '_new': Subquery(model.objects.filter(pk=OuterRef('pk')).values(field_name + '__user')[:1])
})
```

3. Delete all the old fields and model
4. Rename all the new fields and remove pre/postfixes. Optionally rename the new model as well, but don't forget to keep
   the database table name (`class Meta: db_table = 'module_model'`).
5. If you decided not to rename everything back to original names, you will need to replace all the references
   throughout your code. If you're not into `DRY <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_, you might
   consider renaming as a less painful option. Having tests wiull help A LOT here.

You will now end up with a new model that replaces your old one. Of course, the entire procedure is only worth it if you
have code from project base you like and would like to take advantage of. Code such as user merging, maintenance,
profile editor, etc. Regardless, it's a pain taking a bit of time to solve. On the plus side: it's an opportunity for a
bit of a refactoring that's long overdue anyway :D Actually this was written as I (one of the authors of the library)
was converting one of our oldest projects to the new system. I think I just despaired and moaned for a couple of days
before actually doing it in about two hours (I decided NOT to rename the new model and took advantage of the refactoring
opportunity)...


# Notifications

## What is notifications module?

Notifications module will provide functionality to create and deliver notifications to users via channels like: email,
websocket, push notification,..
Currently only maintenance notifications are implemented.

## Maintenance notifications

### Description

When we have a planned server downtime to upgrade or some such, we need to somehow notifiy the users.
But before maintenance occurs, the app itself must also notify the users that server will soon
be down for maintenance.
This notifications is presented to users 8 hours before planned downtime, 1 hour before planned
downtime, 5 minutes before server is going offline.

In order to achieve that we can create a maintenance notification via REST api
described in `Swagger UI </schema/swagger-ui/#/maintenance-notification/maintenance_notification_create>`_. If we have
django project base titlebar UI component integrated into our web UI this component will display
notifications for planned maintenance in above described intervals.

### Installation

Add app to your installed apps.

```python

   # myproject/settings.py

   INSTALLED_APPS = [
    ...
    'django_project_base.notifications',
    ]
```


Add django-project-base notifications urls:

```python

   # url.py

   urlpatterns = [
       ......
       path('', include(notifications_router.urls)),
       ......
   ]
```

Run migrations:

```bash
$ python manage.py migrate
```








## Authentication

### Obtaining and maintaining sessions

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

### Activate project base accounts API endpoints

```python
urlpatterns = [
    path('account/', include('django_project_base.account.urls')),
    #...
]
```

### Session middleware

To enable project base SessionMiddleware, replace Django contrib SessionMiddleware with project base SessionMiddleware in projects settings.py file. This is only necessary if you intend to support the JSON method for login
and keeping the session id.

```python
MIDDLEWARE = [
  #...
  'django_project_base.account.SessionMiddleware',
  #...
]
```

### Use of json session id in subsequent requests

When using  the Authorisation header, use returned session api as token with token type "sessionid" and returned sessionid
as credentials.

```python

  Authorization: sessionid <credentials>
```



### Impersonate user

Sometimes is useful if we can login into app as another user for debugging or help purposes.
User change is supported via REST api calls or you can use userProfile component (django_project_base/templates/user-profile/bootstrap/template.html)
which already integrates api functionality. Functionality is based on django-hijack package.

For determining which user can impersonate which user you can set your own logic. Procedure is described in
https://django-hijack.readthedocs.io/en/stable/configuration/ (See "Custom authorization function") By default
only superusers are allowed to hijack other users.

Example below:

```python

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
```

### User caching backend

To increase AUTH performance you can set a backend that caches users.

To enable User caching backend replace django.contrib.auth.backends.ModelBackend with the following line to
*AUTHENTICATION_BACKENDS* section in settings.py:

```python

   # myproject/settings.py

   AUTHENTICATION_BACKENDS = (
       ...
       'django_project_base.base.auth_backends.UsersCachingBackend',
       ...
   )
```

User caching does not work on bulk updates as Django doesn't trigger signals on update(), bulk_update() or delete().
Bulk updating user profiles without manually clearing cache for them will create stale cache entries, so make sure you
clear any such cache entries manually using the provided :code:`user_cache_invalidate` function.

Example for clearing cache after bulk update:

```python

  ...
  from django.core.cache import cache
  from django_project_base.base.auth_backends import user_cache_invalidate
  ...
  # Bulk update multiple users. Give them superuser permission.
  # If those users are logged in, they don't have permission until cache is
  # cleared or they log out and log in again.
  UserProfile.objects.filter(username__in=['miha', 'janez'])\
      .update(is_superuser=True, is_staff=True)

  # After clearing users cache for those users will be able
  # to work with additional permissions
  staff = UserProfile.objects.filter(username__in=['miha', 'janez'])
  for user in staff:
      user_cache_invalidate(user)
```

It is possible to add a clear cache option also for bulk updates if needed with a custom QuerySet manager.
Example code below.

```python

  # models.py
  ...
  from django.core.cache import cache
  from django_project_base.base.auth_backends import user_cache_invalidate
  ...
  class ProfilesQuerySet(models.QuerySet):
      def update(self, **kwargs):
          for profile in self:
              user_cache_invalidate(profile)
          res = super(ProfilesQuerySet, self).update(**kwargs)
          return res

      def delete(self):
        for profile in self:
            user_cache_invalidate(profile)
        res = super(ProfilesQuerySet, self).delete()
        return res


  class UserProfile(BaseProfile):
      """Use this only for enabling cache clear for bulk update"""
      objects = ProfilesQuerySet.as_manager()
  ...
```

### Social auth integrations

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


### Installation

 Add app to your installed apps.

```python

    # myproject/settings.py

    from django_project_base.accounts import ACCOUNT_APP_ID

    INSTALLED_APPS = [
        ...
        'social_django',
        ACCOUNT_APP_ID,
        ...
     ]
```

 Make sure you have django project base urls included:

```python

    # url.py

    urlpatterns = [
      .....
      path('account/', include(accounts_router.urls)),
      path('account/social/', include('social_django.urls', namespace="social")),
      .....
   ]
```

 Run migrations:

```bash
$ python manage.py migrate
```


### Social login integration example - Google

To enable a social provider create an account at provider webpage and create an oauth app. For example for Google OAuth
login visit https://console.developers.google.com/apis/credentials. Click + CREATE CREDENTIALS and select
Oauth Client ID. Then create OAuth app with OAuth Consent screen.

Example value for Authorized JavaScript origins can be http://localhost:8080.

Example value for Authorized redirect URIs can be http://localhost:8080/account/social/complete/google-oauth2/.

To enable Google OAuth login add folowing to settings:

```python
    # myproject/settings.py
    # enable google social login
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '*Client ID*'
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '*Client secret*'
```
