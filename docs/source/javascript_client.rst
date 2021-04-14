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
