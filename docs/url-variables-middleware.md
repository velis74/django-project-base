# URL variables Middleware

UrlVarsMiddleware will find currently selected project or any other information of interest and add this information
to current request object. At the same time it also serves as global request provider so that you can always access
this information without dragging the request through your APIs.

First, the global request API:

`has_current_request() -> bool`: indicates whether your code was even called through Django middleware pipeline. A
   False return value would indicate a background job such as Celery task or a management command.
`get_current_request() -> WSGIRequest `: returns the request object or raises exception if has_current_request
   returned False

```python
from django_project_base.base.middleware import has_current_request, get_current_request

if has_current_request():
    print(get_current_request().selected_project_slug)
```

The middleware is configured with a setting named `DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES`. Default value for
the setting is:

```python
{
 'project': {'value_name': 'current_project_slug', 'url_part': 'project-'},
 'language': {'value_name': 'current_language', 'url_part': 'language-'},
}
```

The setting is composed of three parts for each individual parsed value. From the 'project' default above:

- name of setting ('project'): this is both the name of the setting as well as identifier of the header to look for. 
  The middleware will be looking for a header named `f"Current-{value_name.lower().title()}"`. In case of 'project'
   default, this means 'Current-Project'. If there is such a header its value will be used for current request.
- value_name ('current_project_slug'): this parameter specifies attribute name into which to store the parsed
   information. In the 'project' default, this will be `session.current_project_slug`.
- url_part ('project-'): This is a "fallback" in case a header is not found. The middleware then parses the URL path
  for `url_part` and if found, the found value will be used. Example: `/project-test/api/v1/get_current_project` would 
  match in the first path segment ('project-test') and `session.current_project_slug` would then be set to `test`.  
  url_part parameter can also be a tuple (integer, List[string]) specifying the path segment that contains project slug
  and segments that are "global" (t.i. not bound to projects). Specifying (1, ('account', 'project')) would  match 
  `test` in `/test/api/v1/get_current_project`, but not `account` in `/account`.

If middleware cannot detect the configured value from headers or path, the variable's `value_name` will be set to
`None`.

```python
# myproject/settings.py

MIDDLEWARE = [
 'django_project_base.base.middleware.UrlsVarsMiddleware',
 ...
]
```
