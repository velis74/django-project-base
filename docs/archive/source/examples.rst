Examples
========

Titlebar component integration example
--------------------------------------

.. code-block:: python

   # define view function, put it in one of urls definition in urls.py
   from django.shortcuts import render

   def index_view(request):
      return render(request=request, template_name='template.html')


.. code-block:: HTML

   <!-- prepare html template template.html -->

    {% load static %}
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Titlebar component example</title>
      {# include django javascript catalog for internationalization #}
      <script src="{% url 'javascript-catalog' %}"></script>
      {# add bootstrap library with dependencies and font-awesome #}
      <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.2/css/all.min.css"
        rel="stylesheet" crossorigin="anonymous">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.js"
        crossorigin="anonymous">
      </script>
      <link
        href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.1/css/bootstrap.css"
        rel="stylesheet" crossorigin="anonymous">
      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"
        crossorigin="anonymous">
      </script>
      {# include django project base js lib and appropriate css #}
      <link href="{% static 'bootstrap_template.css' %}" rel="stylesheet"
        crossorigin="anonymous">
      <script src="{% static 'django-project-base.min.js' %}"></script>
    </head>
    <body>
      {# set div which will contain titlebar component #}
      <div id="titlebar-app" class="titlebar-app">
        {# use/render titlebar component #}
          <titlebar></titlebar>
      </div>
      {# include vue inline template for titlebar component from folder
        coresponding to included css file #}
      {% include "bootstrap/titlebar.html" %}
      <script>
        // initialize titlebar component
        window.djangoProjectBase.createApp('titlebar-app', titlebar);
      </script>
    </body>
    </html>


Example project
===============

You can find examples of most of the functionality of Django project base project in */example/* folder.


Run example project
-------------------

Run Python runserver from root directory of this project and visit url that is provided in command output.

.. code:: bash

  $python manage.py runserver

  ...
  Django version 3.1.8, using settings 'example.setup.settings'
  Starting development server at http://127.0.0.1:8000/
  Quit the server with CONTROL-C.
  ...


Serve Sphinx documentation on localhost
---------------------------------------

Include documentation url to project urls.

.. code-block:: python

   # url.py

   urlpatterns = [
      .....
      re_path(r'^docs-files/(?P<path>.*)$', documentation_view, {'document_root': DOCUMENTATION_DIRECTORY},
            name='docs-files'),
      .....
   ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



Sample data
-----------

**Users**

- **miha**:

  - username: miha
  - password: mihamiha

- **janez**:

  - username: janez
  - password: janezjanez
