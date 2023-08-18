from typing import List

from django.conf import settings
from django.utils.module_loading import import_string

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier


class SmsChannel(Channel):
    id = ChannelIdentifier.SMS.value

    name = "SMS"

    provider = import_string(getattr(settings, "SMS_PROVIDER", ""))

    notification_price = 0.04  # TODO get from settings

    @staticmethod
    def send(notification: "DjangoProjectBaseNotification", extra_data, **kwargs) -> int:  # noqa: F821
        recipients: List[int] = (
            list(map(int, notification.recipients.split(",")))
            if notification.recipients
            else []
        )
        if not recipients or getattr(settings, "TESTING", False):
            return len(recipients)
        SmsChannel.provider().send(notification=notification, extra_data=extra_data)
