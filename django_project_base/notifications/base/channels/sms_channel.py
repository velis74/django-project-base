from typing import List, Union

from django.conf import settings

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.models import DjangoProjectBaseNotification


class SmsChannel(Channel):
    id = ChannelIdentifier.SMS.value

    name = "SMS"

    notification_price = 0.1  # TODO get from settings

    provider_setting_name = "SMS_PROVIDER"

    def get_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        return self._get_sms_message(notification)

    def get_recipients(self, notification: DjangoProjectBaseNotification, unique_identifier=""):
        return list(set(super().get_recipients(notification, unique_identifier="phone_number")))

    def send(self, notification: DjangoProjectBaseNotification, extra_data, **kwargs) -> int:  # noqa: F821
        recipients: List[int] = list(map(int, notification.recipients.split(","))) if notification.recipients else []
        if not recipients or getattr(settings, "TESTING", False):
            return len(recipients)
        return super().send(notification=notification, extra_data=extra_data)
