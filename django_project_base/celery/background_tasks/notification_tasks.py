import logging
import time
from typing import Optional

from django.core.cache import cache

from django_project_base.celery.celery import app
from django_project_base.celery.settings import NOTIFICATION_QUEABLE_HARD_TIME_LIMIT, NOTIFICATION_SEND_PAUSE_SECONDS
from django_project_base.notifications.base.send_notification_mixin import SendNotificationMixin

LAST_MAIL_SENT_CK = "last-notification-was-sent-timestamp"


class SendNotificationTask(app.Task):
    name = "background_tasks.notification_tasks.send_notification_task"

    max_retries = 0
    time_limit = NOTIFICATION_QUEABLE_HARD_TIME_LIMIT
    soft_time_limit = NOTIFICATION_QUEABLE_HARD_TIME_LIMIT - 3
    default_retry_delay = 0

    def run(self, notification: "DjangoProjectBaseNotification", extra_data):  # noqa: F821
        try:
            last_sent: Optional[float] = cache.get(LAST_MAIL_SENT_CK)
            time_from_last_sent: float = time.time() - last_sent if last_sent else 0
            if time_from_last_sent < NOTIFICATION_SEND_PAUSE_SECONDS:
                time.sleep(int(NOTIFICATION_SEND_PAUSE_SECONDS - time_from_last_sent))
            SendNotificationMixin().make_send(notification=notification, extra_data=extra_data)
        finally:
            cache.set(LAST_MAIL_SENT_CK, time.time(), timeout=NOTIFICATION_SEND_PAUSE_SECONDS + 1)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logging.getLogger(__name__).error(
            f"Exception: {exc} \n\nTask id: {task_id}\n\nArgs: {args}\n\nKwargs: {kwargs}\n\nEInfo: {einfo}"
        )


send_notification_task = app.register_task(SendNotificationTask())
