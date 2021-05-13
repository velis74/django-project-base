Performance middleware
======================

Performance middleware module is providing functionality to log and display the summary of the most time-consuming requests.


Installation
------------

To enable middleware add following line to projects settings.py

.. code-block:: python

  # myproject/settings.py

  MIDDLEWARE = [
    ...
    'django_project_base.performance_middleware.middleware.profile_middleware.profile_middleware'
    ...
  ]

View
____

Overview of current state is avialable on url *../app_debug/*