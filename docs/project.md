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

### DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE

```python

DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE: SelectedProjectMode.FULL
```

This setting defines, how project is selected. Options are:
- SelectedProjectMode.FULL
  - Project must be selected in some way before user can work with the app. Either by request url parameters or by 
project selector in titlebar.
- SelectedProjectMode.AUTO
  - This option is for custom implemenstations. It is meant, that there is a custom middleware, that provides selected
project slug. This slug must be set to request attribute that is set in `DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES`
setting for key `project`/`value_name`.
  - Project selector won't be visible in title bar 
- SelectedProjectMode.PROMPT
  - On every table and form that needs project field, this field will be shown and user will have to select project from
projects that he has permission to
  - If user has permission to exactly one project, this project will be preselected. In this case field in tables and 
forms won't be visible
  - Project selector won't be visible in title bar
- Fixed project slug
  - If app actually don't need project there can be only one project in database and its slug can be set to this setting
  - Project selector won't be visible in title bar

Selecting project is done in [SelectProjectMiddleware](./select-project-middleware.md) which is mandatory middleware for
django project base.

