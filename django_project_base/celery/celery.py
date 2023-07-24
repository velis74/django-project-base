import os

from celery import Celery
from kombu import Queue, Exchange

from django_project_base.constants import NOTIFICATION_QUEUE_NAME

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project_base.settings")

app = Celery("django-project-base")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.task_routes = {
    "background_tasks.send_mail_task.* ": {
        "queue": NOTIFICATION_QUEUE_NAME,
        "routing_key": NOTIFICATION_QUEUE_NAME,
    },
}
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

# RUN WORKER AS
# celery -A django-project-base worker --loglevel=ERROR
