from typing import List

from django_project_base.notifications.base.channels.channel import Channel, Recipient
from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.models import DjangoProjectBaseNotification


class SmsChannel(Channel):
    id = ChannelIdentifier.SMS.value

    name = "SMS"

    notification_price = 0.1  # TODO get from settings

    provider_setting_name = "SMS_PROVIDER"

    def get_recipients(self, notification: DjangoProjectBaseNotification, unique_identifier=""):
        return list(set(super().get_recipients(notification, unique_identifier="phone_number")))

    def send(self, notification: DjangoProjectBaseNotification, extra_data, **kwargs) -> int:  # noqa: F821
        return super().send(notification=notification, extra_data=extra_data)

    def clean_sms_recipients(self, recipients: List[Recipient]) -> List[Recipient]:
        return list(filter(lambda r: r.phone_number and len(r.phone_number), self.clean_recipients(recipients)))
