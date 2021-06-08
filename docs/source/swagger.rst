Swagger
=======

Installation
------------

To enable swagger gui, add following to urls.py

.. code-block:: python

  # my_project/urls.py
  urlpatterns = [
    ...
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema', ),
        name='swagger-ui'),
    ...
  ]