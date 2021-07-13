Project
=======

Project API is core part of Django project base.

Project slug
------------

**DJANGO_PROJECT_BASE_SLUG_FIELD_NAME**

When creating models with slug field they should be named with this setting value. This enables that we can use object
slug instead of object pk when making api requests. Default value is "slug".

DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES
----------------------------------------------

.. code-block:: python

    DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES: {
        'project': {'value_name': 'current_project_slug', 'url_part': 'project-'},
        'language': {'value_name': 'current_language', 'url_part': 'language-'}
    }


This setting defines a dictionary of attribute names on the request object. E.g. project info is set on the request
object under property current_project_slug. Language information is set on request objects under property current
language. Is language or project is given in request path like language-EN, then url_part settings is found and EN
string is taken as language value.