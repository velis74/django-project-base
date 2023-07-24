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


accept_content = ["application/json", "application/x-python-serialize", "pickle"]
TASK_SERIALIZER = "json"
RESULT_SERIALIZER = "json"
TIMEZONE = "UTC"
broker_url = f"{redis_location_celery}{'?virtual_host=' + CELERY_REDIS_DB}" if REDIS_LOCATION else ""
SECRET_KEY = get_random_string(length=64)
INSTALLED_APPS = ("django_project_base", "django_project_base.notifications")
