import os

from celery import bootsteps, Celery
from click import Option

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")

app = Celery("django_project_base")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.task_ignore_result = True
app.conf.worker_send_task_events = False

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
