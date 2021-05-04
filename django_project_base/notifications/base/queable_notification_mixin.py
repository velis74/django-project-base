from django_project_base.notifications.models import DjangoProjectBaseNotification


class QueableNotificationMixin(object):
    def enqueue_notification(self, notification: DjangoProjectBaseNotification):
        # prepare code for notification send with right params and put it to queue
        return
