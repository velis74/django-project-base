Notifications
=============

What is notifications module?
-----------------------------

Notifications module will provide functionality to create and deliver notifications to users via channels like: email,
websocket, push notification,..
Currently only maintenance notifications are implemented.

Maintenance notifications
-------------------------

**Description**

When we have a planned server downtime to upgrade or some such, we need to somehow notifiy the users.
But before maintenance occurs, the app itself must also notify the users that server will soon
be down for maintenance.
This notifications is presented to users 8 hours before planned downtime, 1 hour before planned
downtime, 5 minutes before server is going offline.

In order to achieve that we can create a maintenance notification via REST api
described in `Swagger UI </schema/swagger-ui/#/maintenance-notification/maintenance_notification_create>`_. If we have
django project base titlebar UI component integrated into our web UI this component will display
notifications for planned maintenance in above described intervals.

**Installation**

Add app to your installed apps.

.. code-block:: python

   # myproject/settings.py

   INSTALLED_APPS = [
    ...
    'django_project_base.notifications',
    ]


Make sure you have django project base urls included:

.. code-block:: python

   # url.py

   urlpatterns += django_project_base_urlpatterns

Run migrations:

.. code-block:: python

   python manage.py migrate





