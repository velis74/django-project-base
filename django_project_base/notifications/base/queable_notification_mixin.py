import datetime

from django.conf import settings

from django_project_base.celery.background_tasks.notification_tasks import send_notification_task
from django_project_base.celery.settings import NOTIFICATION_SEND_PAUSE_SECONDS, NOTIFICATIONS_QUEUE_VISIBILITY_TIMEOUT
from django_project_base.constants import NOTIFICATION_QUEUE_NAME
from django_project_base.notifications.models import DjangoProjectBaseNotification


class QueableNotificationMixin(object):
    def enqueue_notification(self, notification: DjangoProjectBaseNotification, extra_data):
        if getattr(settings, "TESTING", False):
            return
        now_ts: int = int(datetime.datetime.now().timestamp())
        if notification.delayed_to - now_ts < NOTIFICATION_SEND_PAUSE_SECONDS:
            send_notification_task.apply_async(
                (notification, extra_data), queue=NOTIFICATION_QUEUE_NAME, serializer="pickle"
            )  # type: ignore
            return
        delay: int = notification.delayed_to - now_ts
        if delay > NOTIFICATIONS_QUEUE_VISIBILITY_TIMEOUT:
            raise Exception("Notification delay exceeds permitted delay")
        send_notification_task.apply_async(
            (notification, extra_data),
            eta=datetime.datetime.utcnow() + datetime.timedelta(seconds=delay),
            queue=NOTIFICATION_QUEUE_NAME,
            serializer="pickle",
        )  # type: ignore
