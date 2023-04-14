# Installation

## Django project base

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

Alternatively you can also choose to specify individual URLs. If that's the case, please refer to
django_project_base.urls.py and use only the URLs you need.

::: info

The above general include also includes the Django javascript localisation catalog, so make sure you don't include it
again.

:::

There are some additional URLs available for the Django project base, like swagger or documentation. Appending those
URLs is described in more details in respective chapters.

## Dynamic Forms

Django project base is dependent on Dynamic Forms project https://github.com/velis74/DynamicForms

Read Dynamic Forms documentation for installation steps and more information about project.

You should add at least following code to your project, to enable Dynamic Forms.

::: code-group

```python [myproject/settings.py]

REST_FRAMEWORK = {
...
    'DEFAULT_RENDERER_CLASSES': (
      'rest_framework.renderers.JSONRenderer',
      'rest_framework.renderers.BrowsableAPIRenderer',
      'dynamicforms.renderers.TemplateHTMLRenderer',
      'dynamicforms.renderers.ComponentHTMLRenderer',
      'dynamicforms.renderers.ComponentDefRenderer',
  )
...
}
  
```

:::

## Environment setup

For JS development go to https://nodejs.org/en/ and install latest stable version of nodejs and npm. In {project base
directory}/django_project_base/js_app run:

```bash
$ npm install 
```

To run a development server run:

```bash
$ npm run serve
```

OR:

```bash
$ vite
```

Go to http://localhost:8080/.

To generate a build run:

```bash
$ npm run build
```

JS code is present in src subdirectory. For web UI components library vuejs(https://vuejs.org/) is used with single file
components.

When developing webpack development server expects that service which provides data runs on host
http://127.0.0.1:8000. This can be changed in vue.config.js found in the same directory as package.json. For running
example django project prepare python environment and run {project base directory}:

```bash 
$ pip install -r requirements.txt
$ python manage.py runserver
```

Try logging in with user "miha", pass "mihamiha".

## Activating features

Requires a settings.py `AUTHENTICATION_BACKENDS <https://docs.djangoproject.com/en/dev/topics/auth/customizing/>`_
setting. Optionally also a global cache server such as Redis.
