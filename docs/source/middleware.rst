Middleware
==========

Project Middleware
------------------

ProjectMiddleware: If you wan't to set current project which is selected to request object you can use ProjectMiddleware
which should be placed to start of MIDDLEWARE list in settings.py. Middleware sets DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES
setting dict values to request object. Default value for DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES setting is
{'project': 'current_project_slug', 'language': 'current_language'}.

This means request will have current_project_slug attribute which will have value set to current project slug and request
will have current_language attribute which will have value set to current language set. If project or language cannnot be
determined its value is set to None.

To set current project to ajax requests 'Current-Project' header should be used: 'Current-Project':
'current project slug'. Current slug can also be determined from request path. See
DJANGO_PROJECT_BASE_PROJECT_DEFINED_URL_PART setting description in setting section.

.. code-block:: python

   # myproject/settings.py

   MIDDLEWARE = [
    'django_project_base.base.UrlsVarsMiddleware',
    ...
    ]


Performance profiler
--------------------

Performance profiler module is providing functionality to log and display the summary of the most time-consuming requests.

To enable middleware add following line to project files:

.. code-block:: python

  # myproject/settings.py

  MIDDLEWARE = [
    ...
    'django_project_base.profiling.profile_middleware',
    ...
  ]


  # myproject/urls.py
  from django_project_base.profiling import app_debug_view

  urlpatterns = [
  path('app-debug/', app_debug_view, name='app-debug'),
  ...
  ]

Overview of current state is avialable on url *http://hostname/app_debug/*