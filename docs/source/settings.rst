.. _Settings:

Settings options - quick overview
=================================

**DJANGO_PROJECT_BASE_PROJECT_MODEL**

.. code-block:: python

  DJANGO_PROJECT_BASE_PROJECT_MODEL = 'myapp.MyProject'

Set swappable model for Django project base Project model. Read more in :ref:`Django project base` chapter.

**DJANGO_PROJECT_BASE_PROFILE_MODEL**

.. code-block:: python

  DJANGO_PROJECT_BASE_PROFILE_MODEL = 'myapp.MyProfile'

Set swappable model for Django project base Profile model. Read more in :ref:`Django project base` chapter.

**DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES**

.. code-block:: python

    DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES: {
        'project': {'value_name': 'current_project_slug', 'url_part': 'project-'},
        'language': {'value_name': 'current_language', 'url_part': 'language-'}
    }

A dictionary of attribute names on the request object. Read more in
:ref:`DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES` chapter.

**DJANGO_PROJECT_BASE_SLUG_FIELD_NAME**

.. code-block:: python

    DJANGO_PROJECT_BASE_SLUG_FIELD_NAME: 'slug'

Read more in :ref:`Project slug` chapter.

**MAINTENENACE_NOTIFICATIONS_CACHE_KEY**

.. code-block:: python

  MAINTENENACE_NOTIFICATIONS_CACHE_KEY=""

Read more in :ref:`Maintenance notifications` chapter.

**MAINTENENACE_NOTIFICATIONS_USE_CACHED_QUERYSET**

.. code-block:: python

  MAINTENENACE_NOTIFICATIONS_USE_CACHED_QUERYSET=<bool>

Maintenance notifications use cached queryset. Default is True.

Read more in :ref:`Maintenance notifications` chapter.

**DJANGO_USER_CACHE**

.. code-block:: python

  DJANGO_USER_CACHE='django-user-%d'

Key name for user caching background. Default value is 'django-user-%d'. Read more in :ref:`User caching backend`
chapter.

**CACHE_IMPERSONATE_USER**

.. code-block:: python

  CACHE_IMPERSONATE_USER = 'impersonate-user-%d'

Cache key name for impersonate user. Default value is 'impersonate-user-%d'. Read more in :ref:`Impersonate user`
chapter.

**PROFILE_REVERSE_FULL_NAME_ORDER**

.. code-block:: python

  PROFILE_REVERSE_FULL_NAME_ORDER = (bool)

Read more in :ref:`Profile reverse name order` chapter.

**DELETE_PROFILE_TIMEDELTA**

.. code-block:: python

  DELETE_PROFILE_TIMEDELTA = 0

Value in days, when the automatic process should delete profile marked as for delete. Read more in
:ref:`Deleting profile` chapter.

**DOCUMENTATION_DIRECTORY**

.. code-block:: python

  DOCUMENTATION_DIRECTORY='/docs/build/'

Path for documentation directory. Read more in :ref:`Documentation` chapter.

