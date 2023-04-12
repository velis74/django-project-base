Open Api
========

Add folloving to settings.py

.. code-block:: python

  # myapp/settings.py
  REST_FRAMEWORK = {
  ...
  'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
  ...
  }