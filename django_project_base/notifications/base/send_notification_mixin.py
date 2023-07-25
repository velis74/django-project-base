import logging

from django.utils import timezone

from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.models import DjangoProjectBaseNotification


class SendNotificationMixin(object):
    def make_send(self, notification: DjangoProjectBaseNotification, extra_data) -> DjangoProjectBaseNotification:
        sent_channels: list = []
        failed_channels: list = []
        exceptions = ""
        if notification.required_channels is None:
            return notification
        for channel_identifier in map(
            int, filter(lambda i: not (i is None), notification.required_channels.split(","))
        ):
            channel = ChannelIdentifier.channel(channel_identifier)
            try:
                channel.send(notification, extra_data)
                sent_channels.append(channel)
            except Exception as e:
                logging.getLogger(__name__).error(e)
                failed_channels.append(channel)
                exceptions += f"{str(e)}\n\n"

        if notification.pk:
            notification.sent_channels = (
                ",".join(
                    list(map(lambda f: str(f), filter(lambda d: d is not None, map(lambda c: c.id, sent_channels))))
                )
                if sent_channels
                else None
            )
            notification.failed_channels = (
                ",".join(
                    list(map(lambda f: str(f), filter(lambda d: d is not None, map(lambda c: c.id, failed_channels))))
                )
                if failed_channels
                else None
            )
            notification.sent_at = timezone.now().timestamp()
            notification.exceptions = exceptions if exceptions else None
            notification.save(update_fields=["sent_at", "sent_channels", "failed_channels", "exceptions"])
        return notification
