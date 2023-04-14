# Settings options - quick overview

## DJANGO_PROJECT_BASE_PROJECT_MODEL

```python
DJANGO_PROJECT_BASE_PROJECT_MODEL = 'myapp.MyProject'
```

Set swappable model for Django project base Project model.

## DJANGO_PROJECT_BASE_PROFILE_MODEL

```python
DJANGO_PROJECT_BASE_PROFILE_MODEL = 'myapp.MyProfile'
```

Set swappable model for Django project base Profile model.

## DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES

```python
DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES: {
    'project': {'value_name': 'current_project_slug', 'url_part': 'project-'},
    'language': {'value_name': 'current_language', 'url_part': 'language-'}
}
```

A dictionary of attribute names on the request object. 

## DJANGO_PROJECT_BASE_SLUG_FIELD_NAME

```python
DJANGO_PROJECT_BASE_SLUG_FIELD_NAME: 'slug'
```

## MAINTENANCE_NOTIFICATIONS_CACHE_KEY

```python
MAINTENANCE_NOTIFICATIONS_CACHE_KEY=""
```


## USER_CACHE_KEY

```python
USER_CACHE_KEY = 'django-user-{id}'
```

Key name for user caching background. Default value is 'django-user-{id}'. 

## CACHE_IMPERSONATE_USER

```python
CACHE_IMPERSONATE_USER = 'impersonate-user-%d'
```

Cache key name for impersonate user. Default value is 'impersonate-user-%d'. 

## PROFILE_REVERSE_FULL_NAME_ORDER

```python
PROFILE_REVERSE_FULL_NAME_ORDER = (bool)
```


## DELETE_PROFILE_TIMEDELTA

```python
DELETE_PROFILE_TIMEDELTA = 0
```

Value in days, when the automatic process should delete profile marked as for delete. 

## DOCUMENTATION_DIRECTORY

```python
DOCUMENTATION_DIRECTORY='/docs/build/'
```

Path for documentation directory.

## PROFILER_LONG_RUNNING_TASK_THRESHOLD

```python
PROFILER_LONG_RUNNING_TASK_THRESHOLD = 1000
```

Define treshold in ms for profiling long running tasks.
