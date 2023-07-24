import os

from celery import Celery
from kombu import Queue, Exchange
from django_project_base.constants import NOTIFICATION_QUEUE_NAME


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "celery.settings")

import os

from django.utils.crypto import get_random_string

REDIS_LOCATION = ""
CELERY_REDIS_DB = "3"
redis_location_celery = ""

if os.path.exists("/var/run/redis/redis-server.sock"):
    REDIS_LOCATION = "/var/run/redis/redis-server.sock"

if REDIS_LOCATION:
    redis_location_celery = f"redis+socket://{REDIS_LOCATION}"
    CELERY_BROKER_URL = f"{redis_location_celery}{'?virtual_host=' + CELERY_REDIS_DB}"


class CelerySettings:
    accept_content = ["application/json", "application/x-python-serialize", "pickle"]
    TASK_SERIALIZER = "json"
    RESULT_SERIALIZER = "json"
    TIMEZONE = "UTC"
    broker_url = f"{redis_location_celery}{'?virtual_host=' + CELERY_REDIS_DB}" if REDIS_LOCATION else ""
    SECRET_KEY = get_random_string(length=64)
    INSTALLED_APPS = (
        "django_project_base",
        "django_project_base.notifications",
        "django.contrib.contenttypes",
        "django.contrib.auth",
    )


app = Celery(
    "django_project_base",
    config_source=CelerySettings(),
    include=[
        "django_project_base.celery.background_tasks.notification_tasks",
    ],
)
# app.config_from_object(CelerySettings(), namespace="CELERY")
# app.conf.task_routes = {
#     "background_tasks.notification_tasks.*": {
#         "queue": NOTIFICATION_QUEUE_NAME,
#         "routing_key": NOTIFICATION_QUEUE_NAME,
#     },
# }
app.conf.task_queues = [
    Queue(
        NOTIFICATION_QUEUE_NAME,
        Exchange("transient", delivery_mode=1),
        routing_key=NOTIFICATION_QUEUE_NAME,
        durable=False,
    ),
]

app.conf.task_ignore_result = True
app.conf.worker_send_task_events = False
# apps.populate(CelerySettings().INSTALLED_APPS)

import django
from django.apps import apps

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project_base.celery.settings")
apps.populate(CelerySettings().INSTALLED_APPS)
# django.setup()

# RUN WORKER AS
# celery -A django-project-base worker --loglevel=ERROR -E
