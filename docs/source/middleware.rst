Middleware
==========

URL variables Middleware
------------------------

UrlVarsMiddleware will find currently selected project or any other information of interest and add this information
to current request object. At the same time it also serves as global request provider so that you can always access
this information without dragging the request through your APIs.

First, the global request API:

`has_current_request() -> bool`: indicates whether your code was even called through Django middleware pipeline. A
   False return value would indicate a background job such as Celery task or a management command.
`get_current_request() -> WSGIRequest `: returns the request object or raises exception if has_current_request
   returned False

.. code-block:: python

   from django_project_base.base.middleware import has_current_request, get_current_request

   if has_current_request():
       print(get_current_request().current_project_slug)

The middleware is configured with a setting named `DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES`. Default value for
the setting is:

.. code-block:: python

   {
     'project': {'value_name': 'current_project_slug', 'url_part': 'project-'},
     'language': {'value_name': 'current_language', 'url_part': 'language-'},
   }

The setting is composed of three parts for each individual parsed value. From the 'project' default above:

* name of setting ('project'): this is both the name of the setting as well as identifier of the header to look for.
   The middleware will be looking for a header named `f"Current-{value_name.lower().title()}"`. In case of 'project'
   default, this means 'Current-Project'. If there is such a header its value will be used for current request.
* value_name ('current_project_slug'): this parameter specifies attribute name into which to store the parsed
   information. In the 'project' default, this will be `session.current_project_slug`.
* url_part ('project-'): This is a "fallback" in case a header is not found. The middleware then parses the URL path
   for `url_part` and if found, the found value will be used. Example: `/project-test/api/v1/get_current_project` would
   match in the first path segment ('project-test') and `session.current_project_slug` would then be set to `test`.

   url_part parameter can also be an integer specifying the path segment that contains project slug. Specifying 1 would
   match `test` in `/test/api/v1/get_current_project`.

If middleware cannot detect the configured value from headers or path, the variable's `value_name` will be set to
`None`.

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

Overview of current state is available on url *http://hostname/app-debug/*

Performance profiler can be used to profile any function as long as the function is triggered by input request.

Example below:

.. code-block:: python

    # func variable marks the function name which we want to profile during request
    func = 'name_of_function_to_be_executed'
    from django_project_base.profiling.middleware import ProfileRequest
    # we set profiling path to function name instead of default request path used in profiling.middleware
    ProfileRequest({'REQUEST_METHOD': 'GET', 'HTTP_HOST': '', 'QUERY_STRING': '', 'PATH_INFO': ''},
                   None, (), {})._set_profiling_path(func, '')
    # function is called
    res = globals()[func](**parameters)
    # function finishes and on request end(response) profiling data is logged and it can be then viewed in http://hostname/app-debug/ view
