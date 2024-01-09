import logging

from typing import Optional

from django.conf import Settings
from django.db import connections
from django.db.utils import load_backend

from django_project_base.celery.celery import app
from django_project_base.celery.settings import NOTIFICATION_QUEABLE_HARD_TIME_LIMIT
from django_project_base.constants import NOTIFICATION_QUEUE_NAME

LAST_MAIL_SENT_CK = "last-notification-was-sent-timestamp"


class BaseTask(app.Task):
    name = ""

    max_retries = 0
    time_limit = NOTIFICATION_QUEABLE_HARD_TIME_LIMIT
    soft_time_limit = NOTIFICATION_QUEABLE_HARD_TIME_LIMIT - 3
    default_retry_delay = 0

    settings: Optional[Settings] = None

    def before_start(self, task_id, args, kwargs):
        if (path := self._app.conf.get("django-settings-module")) and len(path):
            self.settings = Settings(path)
            db_settings: dict = self.settings.DATABASES["default"]
            db_settings.setdefault("TIME_ZONE", None)
            db_settings.setdefault("CONN_HEALTH_CHECKS", None)
            db_settings.setdefault("CONN_MAX_AGE", 0)
            db_settings.setdefault("OPTIONS", {})
            db_settings.setdefault("AUTOCOMMIT", True)
            backend = load_backend(db_settings["ENGINE"])
            dw = backend.DatabaseWrapper(db_settings)
            dw.connect()
            connections.databases[NOTIFICATION_QUEUE_NAME] = dw.settings_dict
            connections.databases["default"] = dw.settings_dict

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logging.getLogger(__name__).error(
            f"Exception: {exc} \n\nTask id: {task_id}\n\nArgs: {args}\n\nKwargs: {kwargs}\n\nEInfo: {einfo}"
        )

    def run(self, *args, **kwargs):
        return None
