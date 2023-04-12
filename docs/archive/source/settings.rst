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

**MAINTENANCE_NOTIFICATIONS_CACHE_KEY**

.. code-block:: python

  MAINTENANCE_NOTIFICATIONS_CACHE_KEY=""

Read more in :ref:`Maintenance notifications` chapter.

**USER_CACHE_KEY**

.. code-block:: python

  USER_CACHE_KEY = 'django-user-{id}'

Key name for user caching background. Default value is 'django-user-{id}'. Read more in :ref:`User caching backend`
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

Path for documentation directory.

**PROFILER_LONG_RUNNING_TASK_THRESHOLD**

.. code-block:: python

  PROFILER_LONG_RUNNING_TASK_THRESHOLD = 1000

Define treshold in ms for profiling long running tasks. Read more in :ref:`Performance profiler`
chapter.
