from django_project_base.notifications.models import DjangoProjectBaseNotification
from django_project_base.constants import NOTIFICATION_QUEUE_NAME


class QueableNotificationMixin(object):
    def enqueue_notification(self, notification: DjangoProjectBaseNotification):
        send_notification_task.apply_async((notification,), queue=NOTIFICATION_QUEUE_NAME, serializer="pickle")  # type: ignore
