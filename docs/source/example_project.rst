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