# Installation

## Django project base

To install the package, run the following command:

```bash
$ pip install django-project-base
```

To use the library, extend the BaseProject and BaseProfile models in your app's models.py file:

::: code-group

```python [myapp/models.py]

from django_project_base import BaseProject

class MyProject(BaseProject):
    # add any fields and methods you like here

class MyProfile(BaseProfile):
    # add any fields and methods you like here
    
```

:::

Django Project Base utilizes Swapper (https://pypi.org/project/swapper/), an unofficial API for Django swappable models.
Before you can use the library, you must override the Project, Profile and Tag models as there are no migrations included in
the library. The library only declares the properties it supports, but you have the option to extend them as needed to
fit your project's requirements.

Make sure to load your swappable models instead of the django-project-base models in your settings.py file:

::: code-group

```python [myproject/settings.py]
DJANGO_PROJECT_BASE_PROJECT_MODEL = 'myapp.MyProject'
DJANGO_PROJECT_BASE_PROFILE_MODEL = 'myapp.MyProfile'

```

:::

Add the following to your INSTALLED_APPS:

::: code-group

```python [myproject/settings.py]
INSTALLED_APPS = [
# ...
    'rest_registration',
    'django_project_base',
    'drf_spectacular',
# ...
]
```

:::

Include the following settings for REST_FRAMEWORK and REST_REGISTRATION:

::: code-group

```python [myproject/settings.py]
REST_FRAMEWORK = {
# YOUR SETTINGS
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

REST_REGISTRATION = {
    "REGISTER_VERIFICATION_ENABLED": False,
    "REGISTER_EMAIL_VERIFICATION_ENABLED": False,
    "RESET_PASSWORD_VERIFICATION_ENABLED": False,
    "LOGIN_DEFAULT_SESSION_AUTHENTICATION_BACKEND": "django_project_base.base.auth_backends.UsersCachingBackend",
}

```

:::

Append the django project base URLs to your project's urls.py file:

::: code-group

```python [myproject/urls.py]
urlpatterns = [
    ...
    path('', include('django_project_base.urls')),
    ...
]
```

:::

Alternatively, you can specify individual URLs. Refer to django_project_base.urls.py and include only the URLs you need.

::: info

Note that the general include above also includes the Django JavaScript localization catalog, so be sure not to include
it again.

:::

Additional URLs are available for the Django project base, such as Swagger or documentation. Details on appending those
URLs can be found in their respective chapters."

## Dynamic Forms

Django Project Base is dependent on the Dynamic Forms project (https://github.com/velis74/DynamicForms).

Please refer to the Dynamic Forms documentation for installation steps and more information about the project.

To enable Dynamic Forms, you should add the following code to your project:

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

This code adds the Dynamic Forms renderers to your REST framework settings.

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

We're using a visualisation library called Vuetify. Make sure you load the icons and font in your project:

index.html
```HTML
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:100,300,400,500,700,900">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@mdi/font@latest/css/materialdesignicons.min.css">
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
