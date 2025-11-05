import os

from celery import bootsteps, Celery
from click import Option
from kombu import Exchange, Queue
from kombu.entity import TRANSIENT_DELIVERY_MODE

from django_project_base.celery.settings import NOTIFICATIONS_QUEUE_VISIBILITY_TIMEOUT
from django_project_base.constants import NOTIFICATION_QUEUE_NAME

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")

app = Celery(
    "django_project_base",
    include=[
        "django_project_base.celery.background_tasks.notification_tasks",
    ],
)
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.task_queues = [
    Queue(
        NOTIFICATION_QUEUE_NAME,
        Exchange("transient", delivery_mode=TRANSIENT_DELIVERY_MODE),
        routing_key=NOTIFICATION_QUEUE_NAME,
        durable=False,
    ),
]

app.conf.beat_schedule = {
    "scheduler": {
        "task": "background_tasks.notification_tasks.notification_scheduler_task",
        "schedule": 3,
        "options": {"queue": "notification"},
    },
}

app.conf.task_ignore_result = True
app.conf.worker_send_task_events = False
app.conf.broker_transport_options = {"visibility_timeout": NOTIFICATIONS_QUEUE_VISIBILITY_TIMEOUT}
setting_option = Option(("--settings",), is_flag=False, help="Django settings file path", default="")
app.user_options["worker"].add(setting_option)
app.user_options["beat"].add(setting_option)


class CeleryBootstep(bootsteps.Step):
    def __init__(self, parent, **options):
        super().__init__(parent, **options)
        app.conf.setdefault("django-settings-module", options.get("settings", ""))


app.steps["worker"].add(CeleryBootstep)
app.steps["beat"].add(CeleryBootstep)

# RUN WORKER AS
# celery -A django_project_base.celery.celery worker -l INFO -Q notification --concurrency=1
