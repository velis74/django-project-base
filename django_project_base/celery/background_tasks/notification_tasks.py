import time

from typing import Optional

from django import db
from django.core.cache import cache

from django_project_base.celery.background_tasks.base_task import BaseTask
from django_project_base.celery.celery import app
from django_project_base.celery.settings import NOTIFICATION_QUEABLE_HARD_TIME_LIMIT, NOTIFICATION_SEND_PAUSE_SECONDS
from django_project_base.notifications.base.send_notification_service import SendNotificationService

LAST_MAIL_SENT_CK = "last-notification-was-sent-timestamp"


class SendNotificationTask(BaseTask):
    name = "background_tasks.notification_tasks.send_notification_task"

    max_retries = 0
    time_limit = NOTIFICATION_QUEABLE_HARD_TIME_LIMIT
    soft_time_limit = NOTIFICATION_QUEABLE_HARD_TIME_LIMIT - 3
    default_retry_delay = 0

    def run(self, notification: "DjangoProjectBaseNotification", extra_data):  # noqa: F821
        super().run()
        try:
            last_sent: Optional[float] = cache.get(LAST_MAIL_SENT_CK)
            time_from_last_sent: float = time.time() - last_sent if last_sent else 0
            if time_from_last_sent < NOTIFICATION_SEND_PAUSE_SECONDS:
                time.sleep(int(NOTIFICATION_SEND_PAUSE_SECONDS - time_from_last_sent))
            SendNotificationService(settings=self.settings).make_send(notification=notification, extra_data=extra_data)
        finally:
            cache.set(LAST_MAIL_SENT_CK, time.time(), timeout=NOTIFICATION_SEND_PAUSE_SECONDS + 1)
            db.connections.close_all()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super().on_failure(exc=exc, task_id=task_id, args=args, kwargs=kwargs, einfo=einfo)


send_notification_task = app.register_task(SendNotificationTask())
