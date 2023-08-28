from django.conf import settings
from django.db.models.functions import Length
from django.utils import timezone

from django_project_base.notifications.models import DjangoProjectBaseNotification


class DuplicateNotificationMixin(object):
    def handle_similar_notifications(self, notification: DjangoProjectBaseNotification) -> bool:
        message_length: int = len(notification.message.body)
        sent_notifications = (
            DjangoProjectBaseNotification.objects.annotate(message_len=Length("message__body"))
            .filter(
                content_entity_context=notification.content_entity_context,
                created_at__gt=timezone.now().timestamp() - settings.NOTIFICATION_AGGREGATION_TIMEDELTA_SECONDS,
                level=notification.level,
                type=notification.type,
                recipients=notification.recipients,
                required_channels=notification.required_channels,
                message_len__gte=message_length - settings.NOTIFICATION_LENGTH_SIMILARITY_BUFFER_VALUE,
                message_len__lte=message_length + settings.NOTIFICATION_LENGTH_SIMILARITY_BUFFER_VALUE,
                message__subject=notification.message.subject,
                locale=notification.locale,
            )
            .order_by("-created_at")
        )

        if sent_notifications.exists():
            first_same_notification = sent_notifications.first()
            first_same_notification.counter = first_same_notification.counter + 1
            first_same_notification.save(update_fields=["counter"])
            return True
        return False
