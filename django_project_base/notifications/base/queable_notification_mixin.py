from django_project_base.notifications.models import DjangoProjectBaseNotification
from django_project_base.constants import NOTIFICATION_QUEUE_NAME
from django_project_base.celery.background_tasks.notification_tasks import send_notification_task


class QueableNotificationMixin(object):
    def enqueue_notification(self, notification: DjangoProjectBaseNotification):
        send_notification_task.apply_async((notification,), queue=NOTIFICATION_QUEUE_NAME, serializer="pickle")  # type: ignore
