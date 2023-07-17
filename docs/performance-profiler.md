# Performance profiler

Performance profiler module is providing functionality to log and display the summary of the most time-consuming requests.


To enable middleware add following line to project files:

```python
# myproject/settings.py

MIDDLEWARE = [
...
'django_project_base.profiling.profile_middleware',
...
]
```

```python
  # myproject/urls.py
  from django_project_base.profiling import app_debug_view

  urlpatterns = [
  path('app-debug/', app_debug_view, name='app-debug'),
  ...
  ]
```

Overview of current state is available on url *http://hostname/app-debug/*

Performance profiler can be used to profile any function as long as the function is triggered by input request.

Example below:

```python
# func variable marks the function name which we want to profile during request
func = 'name_of_function_to_be_executed'
from django_project_base.profiling.middleware import ProfileRequest

# we set profiling path to function name instead of default request path used in profiling.middleware
ProfileRequest({'REQUEST_METHOD': 'GET', 'HTTP_HOST': '', 'QUERY_STRING': '', 'PATH_INFO': ''},
               None, (), {})._set_profiling_path(func, '')

# function is called
res = globals()[func](**parameters)

# function finishes and on request end(response) profiling data is logged and it can be then viewed in http://hostname/app-debug/ view
```
