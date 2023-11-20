import os

from celery import Celery, bootsteps
from django.apps import apps
from django.utils.crypto import get_random_string
from kombu import Exchange, Queue
from click import Option
from kombu.entity import TRANSIENT_DELIVERY_MODE

from django_project_base.celery.settings import NOTIFICATIONS_QUEUE_VISIBILITY_TIMEOUT
from django_project_base.constants import NOTIFICATION_QUEUE_NAME

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
        "django_project_base.licensing",
        "django_project_base.notifications",
        "django.contrib.contenttypes",
        "django.contrib.auth",
    )
    TESTING = False


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project_base.celery.settings")
apps.populate(CelerySettings().INSTALLED_APPS)

app = Celery(
    "django_project_base",
    config_source=CelerySettings,
    include=[
        "django_project_base.celery.background_tasks.notification_tasks",
        "django_project_base.celery.background_tasks.beat_task",
    ],
)

app.conf.task_routes = {
    "background_tasks.beat_task.beat_task": {
        "queue": NOTIFICATION_QUEUE_NAME,
        "routing_key": NOTIFICATION_QUEUE_NAME,
    },
}
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
        "task": "background_tasks.beat_task.beat_task",
        # "schedule": 60,
        "schedule": 10,  # TODO: Change to 60
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

# RUN WORKER AS
# celery -A django_project_base.celery.celery worker -l INFO -Q notification --concurrency=1

# RUN BEAT FOR DELAYED NOTIFICATIONS AS
# celery -A django_project_base.celery.celery beat -l INFO
