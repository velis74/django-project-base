from typing import List

from django.conf import settings

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier


class SmsChannel(Channel):
    id = ChannelIdentifier.SMS.value

    name = "SMS"

    notification_price = 0.1  # TODO get from settings

    provider_setting_name = "SMS_PROVIDER"

    @staticmethod
    def send(notification: "DjangoProjectBaseNotification", extra_data, **kwargs) -> int:  # noqa: F821
        recipients: List[int] = list(map(int, notification.recipients.split(","))) if notification.recipients else []
        if not recipients or getattr(settings, "TESTING", False):
            return len(recipients)
        return SmsChannel.provider(extra_settings=extra_data, setting_name=SmsChannel.provider_setting_name).send(
            notification=notification, extra_data=extra_data
        )
