What is django-project-base?
================================

We start with a project. Everything revolves around it: users, roles, permissions, tags, etc. Everything belongs to a
project first, then to database. This project makes it easy to work on that premise. At the same time it integrates a
few basic operations that you need in every project so that you don't have to do them over and over again.

This is a `django <https://www.djangoproject.com/>`_ library, based on
`django-rest-framework <https://www.django-rest-framework.org/>`_ with
`django-allauth <https://github.com/pennersr/django-allauth>`_ integration.


Why django-project-base?
============================

Functionalities provided:

* A base Project definition and editor for it. Extend as you like.
* User profile editor. Manage emails, confirmations, social connections
* Support for REST-based authentication / session creation
* Session / user caching for speed
* Project users editor. Invite users to project. Assign them into roles.
* Roles management & rights assignment.
* Tags editor & manager + support API for marking tagged items with their colours or icons


Quick start
===========

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


.. warning::

   This is important!!! You need to do the overriding before you create migrations. Migrating after default models had
   been created and used is a really hard and painful process. So make triple sure you don't deploy your application
   without first making sure the model you want to use is either your own or you are satisfied with our default
   implementation.

JavaScript code style:
    Use settings in .jshintrc file present in repository. Set tab size, ident, continuation ident in your editor to 2 places.