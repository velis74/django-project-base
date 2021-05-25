Installation
============

Install the package:

.. code-block:: bash

   pip install django-project-base


Extend the BaseProject & BaseProfile model:

.. code-block:: python

   # myapp/models.py
   from django_project_base import BaseProject

   class MyProject(BaseProject):
       # add any fields & methods you like here

   class MyProfile(BaseProfile):
       # add any fields & methods you like here



Then also make sure your models are loaded instead of django-project-base models:

.. code-block:: python

   # myproject/settings.py

   DJANGO_PROJECT_BASE_PROJECT_MODEL = 'myapp.MyProject'
   DJANGO_PROJECT_BASE_PROFILE_MODEL = 'myapp.MyProfile'

   # urls.py add
   from django_project_base.router import django_project_base_urlpatterns
   urlpatterns = [ ... ] + django_project_base_urlpatterns

   Add to INSTALLED_APPS
    'rest_registration',
    'django_project_base',
    'drf_spectacular',

   Add:
     REST_FRAMEWORK = {
    # YOUR SETTINGS
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    }


.. warning::

   This is important!!! You need to do the overriding before you create migrations, overriding base class is **mandatory**.
   There arent any migrations available for *default models*. Migrating after models had been created and used is a
   really hard and painful process. So make triple sure you don't deploy your application without first making sure the
   model you want to use is either your own or you are satisfied with our default implementation.

Append django project base urls:

.. code-block:: python

  # myproject/urls.py
  urlpatterns = [
    ...
    path('', include('django_project_base.urls')),
    ...
  ]

There are some additional URLs available for the Django project base, like swagger or documentation. Appending those
URLs is described in more details in suitable chapters.

Dynamic Forms
-------------

Django project base is dependent on Dynamic Forms project https://github.com/velis74/DynamicForms

Read Dynamic Forms documentation for installation steps and more information about project.

You should add at least following code to your project, to enable Dynamic Forms.

.. code-block:: python

  # myproject/settings.py

  REST_FRAMEWORK = {
  ...
        'DEFAULT_RENDERER_CLASSES': (
          'rest_framework.renderers.JSONRenderer', 'rest_framework.renderers.BrowsableAPIRenderer',
          'dynamicforms.renderers.TemplateHTMLRenderer',
      )
  ...
  }