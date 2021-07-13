.. _Settings:
Settings options - quick overview
=================================

**DJANGO_PROJECT_BASE_PROJECT_MODEL**

.. code-block:: python

  DJANGO_PROJECT_BASE_PROJECT_MODEL = 'myapp.MyProject'

Set swappable model for Django project base Project model. Read more in :ref:`Installation` chapter.

**DJANGO_PROJECT_BASE_PROFILE_MODEL**

.. code-block:: python

  DJANGO_PROJECT_BASE_PROFILE_MODEL = 'myapp.MyProfile'

Set swappable model for Django project base Profile model. Read more in :ref:`Installation` chapter.

**DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES**

.. code-block:: python

    DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES: {
        'project': {'value_name': 'current_project_slug', 'url_part': 'project-'},
        'language': {'value_name': 'current_language', 'url_part': 'language-'}
    }


This setting defines dictionary of attribute names on request object. For e.g. project info is set on request object under
propery current_project_slug. Language information is set on request objects under property current language. Is language
or project is given in request path like: language-EN, then url_part settings is found and EN string is taken as language value.

**DJANGO_PROJECT_BASE_SLUG_FIELD_NAME**

.. code-block:: python

    DJANGO_PROJECT_BASE_SLUG_FIELD_NAME: 'slug'

When creating models with slug field they should be named with this setting value. This enables that we can use object slug instead of
object pk when making api requests.

**MAINTENENACE_NOTIFICATIONS_CACHE_KEY**

.. code-block:: python

  MAINTENENACE_NOTIFICATIONS_CACHE_KEY=""

**DJANGO_USER_CACHE**

.. code-block:: python

  DJANGO_USER_CACHE='django-user-%d'

Key name for user caching background. Default value is 'django-user-%d'.

**CACHE_IMPERSONATE_USER**

.. code-block:: python

  CACHE_IMPERSONATE_USER = 'impersonate-user-%d'

Cache key name for impersonate user. Default value is 'impersonate-user-%d'.

**PROFILE_REVERSE_FULL_NAME_ORDER**

.. code-block:: python

  PROFILE_REVERSE_FULL_NAME_ORDER = (bool)

Defines first_name, last_name order for readonly field *full_name*. Default order is *False* - "First Last". Changing
setting to true will reverse order to "Last First".

Global setting can be also overrided with profile option reverse_full_name_order (bool).

**DELETE_PROFILE_TIMEDELTA**

.. code-block:: python

  DELETE_PROFILE_TIMEDELTA = 0

How far in future will user profile be actually deleted with automatic process. Value is set in days.

**DOCUMENTATION_DIRECTORY**

.. code-block:: python

  DOCUMENTATION_DIRECTORY='/docs/build/'