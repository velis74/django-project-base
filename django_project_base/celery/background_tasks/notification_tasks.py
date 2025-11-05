import datetime
import time

from typing import Optional

from django.core.cache import cache

from django_project_base.celery.background_tasks.base_task import BaseTask
from django_project_base.celery.celery import app
from django_project_base.celery.settings import NOTIFICATION_QUEABLE_HARD_TIME_LIMIT, NOTIFICATION_SEND_PAUSE_SECONDS
from django_project_base.constants import NOTIFICATION_QUEUE_NAME
from django_project_base.notifications.base.send_notification_service import SendNotificationService
from django_project_base.notifications.models import DjangoProjectBaseNotification
from django_project_base.serialization import CacheLock

LAST_MAIL_SENT_CK = "last-notification-was-sent-timestamp"


class SendNotificationTask(BaseTask):
    name = "background_tasks.notification_tasks.send_notification_task"

    max_retries = 0
    time_limit = NOTIFICATION_QUEABLE_HARD_TIME_LIMIT
    soft_time_limit = NOTIFICATION_QUEABLE_HARD_TIME_LIMIT - 3
    default_retry_delay = 0

    def run(self, notification: "DjangoProjectBaseNotification", extra_data):  # noqa: F821
        with CacheLock(f"notification_send_task_{notification.id}", timeout=-1) as cl:
            cl()
            if DjangoProjectBaseNotification.objects.filter(id=notification.id, done=True).exists():
                return
            try:
                last_sent: Optional[float] = cache.get(LAST_MAIL_SENT_CK)
                time_from_last_sent: float = time.time() - last_sent if last_sent else 0
                if time_from_last_sent < NOTIFICATION_SEND_PAUSE_SECONDS:
                    time.sleep(int(NOTIFICATION_SEND_PAUSE_SECONDS - time_from_last_sent))
                SendNotificationService(settings=self.settings).make_send(
                    notification=notification, extra_data=extra_data
                )
            finally:
                cache.set(LAST_MAIL_SENT_CK, time.time(), timeout=NOTIFICATION_SEND_PAUSE_SECONDS + 1)
        self._close_db()


send_notification_task = app.register_task(SendNotificationTask())


class NotificationSchedulerTask(BaseTask):
    name = "background_tasks.notification_tasks.notification_scheduler_task"

    def run(self):
        from django_project_base.notifications.base.enums import NotificationType

        if getattr(self.settings, "TESTING", False):
            return

        with CacheLock("notification_scheduler_task", timeout=-1) as cl:
            cl()
            for notification in DjangoProjectBaseNotification.objects.filter(
                done=False,
                delayed_to__lte=int(datetime.datetime.now().timestamp()),
                type=NotificationType.STANDARD.value,
            ):
                notification.prepare_for_send()
                send_notification_task.apply_async(
                    (notification, notification.extra_data), queue=NOTIFICATION_QUEUE_NAME, serializer="pickle"
                )

        self._close_db()


notification_scheduler_task = app.register_task(NotificationSchedulerTask())
