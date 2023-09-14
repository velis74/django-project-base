from typing import List

from django.conf import settings

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.models import DjangoProjectBaseNotification


class MailChannel(Channel):
    id = ChannelIdentifier.MAIL.value

    name = "EMail"

    notification_price = 0.0002  # TODO get from settings

    provider_setting_name = "EMAIL_PROVIDER"

    def send(self, notification: DjangoProjectBaseNotification, extra_data, **kwargs) -> int:
        if getattr(settings, "TESTING", False):
            recipients: List[int] = (
                list(map(int, notification.recipients.split(","))) if notification.recipients else []
            )
            return len(recipients)
        return super().send(notification=notification, extra_data=extra_data)
