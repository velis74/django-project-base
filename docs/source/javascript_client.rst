Javascript Client
=================

Usage
------

Look at django_project_base/templates/index.html for examples.

**API Documentation**

Swagger UI is accessible on /schema/swagger-ui/ url by running example project.

**Translations**:

If you want to use your Django translations in your app include <script src="{% url 'javascript-catalog' %}"></script> in
your html document header.

**Titlebar component integration example**

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
        createApp('titlebar-app', titlebar);
      </script>
    </body>
    </html>


For developers
---------------
For code formatting use .jshintrc file present in repository. Set tab size, ident, continuation ident in your editor to 2 places.

For JS development go to https://nodejs.org/en/ and install latest stable version of nodejs and npm.
In project base directory run npm install. To run a development server run npm run dev (go to http://0.0.0.0:8080/).
To generate a build run npm run build.

JS code is present in src directory. For web UI components library vuejs(https://vuejs.org/) is used.
Components are built as Vue global components(https://vuejs.org/v2/guide/components.html)
with x-templates. Templates are present in templates directory.

When developing webpack development server expects that service which provides data runs on host
http://127.0.0.1:8000. This can be changed in webpack.config.js file.
For running example django project prepare python environment and run (run in repository root):

- pip install -r requirements.txt (run in content root)
- python manage.py runserver

Try logging in with user "miha", pass "mihamiha".
