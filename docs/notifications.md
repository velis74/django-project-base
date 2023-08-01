
# Notifications

## What is notifications module?

Notifications module will provide functionality to create and deliver notifications to users via channels like: email,
websocket, push notification,..
Currently only maintenance and email notifications are supported. For email Amazon SES provider is implemented.

## Maintenance notifications

### Description

When we have a planned server downtime to upgrade or some such, we need to somehow notifiy the users.
But before maintenance occurs, the app itself must also notify the users that server will soon
be down for maintenance.
This notifications is presented to users 8 hours before planned downtime, 1 hour before planned
downtime, 5 minutes before server is going offline.

In order to achieve that we can create a maintenance notification via REST api
described in `Swagger UI </schema/swagger-ui/#/maintenance-notification/maintenance_notification_create>`_. If we have
django project base titlebar UI component integrated into our web UI this component will display
notifications for planned maintenance in above described intervals.

### Installation

Add app to your installed apps.

```python

   # myproject/settings.py

   INSTALLED_APPS = [
    ...
    'django_project_base.notifications',
    ]
```


Add django-project-base notifications urls:

```python

   # url.py

   urlpatterns = [
       ......
       path('', include(notifications_router.urls)),
       ......
   ]
```

Run migrations:

```bash
$ python manage.py migrate
```



## Settings

#### MAINTENANCE_NOTIFICATIONS_CACHE_KEY

```python

# Maintenance notifications cache key value. User acknowledged 
# maintenance notifications are saved under this cache key value.

MAINTENANCE_NOTIFICATIONS_CACHE_KEY = ""
```

#### NOTIFICATION_AGGREGATION_TIMEDELTA_SECONDS

```python

# Django Project Base system tries to detect duplicate notifications. For time interval in last
# NOTIFICATION_AGGREGATION_TIMEDELTA_SECONDS value it tries to search for notification duplicate and if found
# then notification is not sent, but found notification counter is incremented.

NOTIFICATION_AGGREGATION_TIMEDELTA_SECONDS = 120
```

#### NOTIFICATION_LENGTH_SIMILARITY_BUFFER_VALUE

```python

# Django Project Base system tries to detect duplicate notifications. When comparing 
# notifications it evaluates also notification body length. If notification duplicates candidates body 
# length are within NOTIFICATION_LENGTH_SIMILARITY_BUFFER_VALUE (length difference is smaller than) 
# NOTIFICATION_LENGTH_SIMILARITY_BUFFER_VALUE then notification body length condition is evaluated true.
# If all other conditions (subject, recipients, channel ...) are evaluated true then notification 
# is marked as a duplicate.

NOTIFICATION_LENGTH_SIMILARITY_BUFFER_VALUE = 3
```
