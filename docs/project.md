# Project

Project API is core part of Django project base.

## Settings

### DJANGO_PROJECT_BASE_PROJECT_MODEL

```python
DJANGO_PROJECT_BASE_PROJECT_MODEL = 'myapp.MyProject'
```

Set swappable model for Django project base Project model.

### DJANGO_PROJECT_BASE_SLUG_FIELD_NAME

```python
DJANGO_PROJECT_BASE_SLUG_FIELD_NAME: 'slug'
```

When creating models with slug field they should be named with this setting value. This enables that we can use object
slug instead of object pk when making api requests. Default value is "slug".

### DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES

```python

DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES: {
        'project': {'value_name': 'current_project_slug', 'url_part': 'project-'},
        'language': {'value_name': 'current_language', 'url_part': 'language-'}
}
```

This setting defines a dictionary of attribute names on the request object. 
See [URL variables Middleware](./url-variables-middleware) for more information.

## Currently selected project

Having specified the `DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES` setting, specifically the "project" section,
[SessionMiddleware](./authentication#session-middleware) will be keeping track of currently selected project and the
following variables will become available for use:

```python
request.selected_project
request.selected_project_slug
```

The former is a `SimpleLazyObject` resolving to currently selected project. The information is also written in the
session data, so not every API call needs to bear project slug in order for the system to know it.

If selected_project cannot evaluate, either because the setting is not set or because the project can't be found,
a `ProjectNotSelectedError` will be raised. The exception derives from `NotImplementedError`, but has a `message` member
in case you might want to throw a more API-friendly error with the same message. DPB itself does this on several 
occasions transforming a `ProjectNotSelectedError` into a 404 - `NotFound`.

Also note that SimpleLazyObject does not evaluate simply by invoking it, e.g. `request.selected_project`. You actually 
have to access one of its members, e.g. 
`request.selected_project.get_deferred_fields()  # force immediate LazyObject evaluation`. If you're trying to catch 
the exception, make sure you force evaluation. There are examples for both forced and "natural" evaluation in DPB code.

The latter (`request.selected_project_slug`) is currently evaluated project slug.

::: warning
`request.selected_project_slug` may not represent a proper project slug. It is just what was evaluated as per
`DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES` setting. If you need a validated slug, use `request.selected_project`
and access it's `slug` field.
:::

::: info
[Task #705](https://taiga.velis.si/project/velis-django-project-admin/us/705) will provide means to annul the above 
warning.
:::
