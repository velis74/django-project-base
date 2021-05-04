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

   This is important!!! You need to do the overriding before you create migrations. Migrating after default models had
   been created and used is a really hard and painful process. So make triple sure you don't deploy your application
   without first making sure the model you want to use is either your own or you are satisfied with our default
   implementation.
