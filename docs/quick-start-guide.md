# Quick start guide

## Introduction

### What is django-project-base?

This project removes the boilerplate associated with project / user handling: We start with a project. Everything
revolves around it: users, roles, permissions, tags, etc. This project makes it easy to work on that premise: it
provides foundations for user profiles, oauth authentication, permissions, projects, tagging, etc.

In order to take advantage of all this, just enable desired middleware and extend the models. This project will take
care of the groundwork while you focus on your own project.

This is a django library, based on django-rest-framework with DynamicForms and Django REST Registration integration.

### Why django-project-base?

Functionalities provided:

- A base Project definition and editor for it. Extend as you like.
- User profile editor. Manage emails, confirmations, social connections
- Support for REST-based authentication / session creation
- Session / user caching for speed
- Project users editor. Invite users to project. Assign them into roles.
- Roles management & rights assignment.
- Tags editor & manager + support API for marking tagged items with their colours or icons
- Various Vue components for visualising the above in browsers

## Installation

### Django project base

Install the package:

```bash
$ pip install django-project-base
```

Extend the BaseProject & BaseProfile model:

::: code-group

```python [myapp/models.py]

from django_project_base import BaseProject

class MyProject(BaseProject):
    # add any fields and methods you like here

class MyProfile(BaseProfile):
    # add any fields and methods you like here
    
```

:::

Django project base uses Swapper https://pypi.org/project/swapper/, an unofficial API for Django swappable models. You
need to override the Project and Profile models before you can use the library: there aren’t any migrations available in
the library itself. The library only declares properties it itself supports, but you have the option to extend them as
you wish to fit your needs too.

Then also make sure your swappable models are loaded instead of django-project-base models:

::: code-group

```python [myproject/settings.py]
DJANGO_PROJECT_BASE_PROJECT_MODEL = 'myapp.MyProject'
DJANGO_PROJECT_BASE_PROFILE_MODEL = 'myapp.MyProfile'

# Add to INSTALLED_APPS
INSTALLED_APPS = [
# ...
    'rest_registration',
    'django_project_base',
    'drf_spectacular',
# ...
]

# Add:
REST_FRAMEWORK = {
# YOUR SETTINGS
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Add:
REST_REGISTRATION = {
    "REGISTER_VERIFICATION_ENABLED": False,
    "REGISTER_EMAIL_VERIFICATION_ENABLED": False,
    "RESET_PASSWORD_VERIFICATION_ENABLED": False,
    "LOGIN_DEFAULT_SESSION_AUTHENTICATION_BACKEND": "django_project_base.base.auth_backends.UsersCachingBackend",
}

```

:::

Append django project base urls:

::: code-group

```python [myproject/urls.py]
urlpatterns = [
    ...
    path('', include('django_project_base.urls')),
    ...
]
```

::: 