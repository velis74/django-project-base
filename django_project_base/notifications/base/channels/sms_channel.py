from typing import List

from django.conf import Settings
from django.utils.translation import gettext_lazy as _

from django_project_base.notifications.base.channels.channel import Channel, Recipient
from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.models import DjangoProjectBaseNotification


class SmsChannel(Channel):
    id = ChannelIdentifier.SMS.value

    name = "SMS"

    notification_price = 0.1  # TODO get from settings

    provider_setting_name = "NOTIFICATIONS_SMS_PROVIDER"

    @property
    def verbose_name(self):
        return _("SMS")

    def get_recipients(
        self, notification: DjangoProjectBaseNotification, unique_identifier="", phone_number_validator=None
    ):
        return list(
            set(
                super().get_recipients(
                    notification, unique_identifier="phone_number", phone_number_validator=phone_number_validator
                )
            )
        )

    def send(self, notification: DjangoProjectBaseNotification, extra_data: dict, settings: Settings, **kwargs) -> int:  # noqa: F821
        return super().send(notification=notification, extra_data=extra_data, settings=settings)

    def clean_sms_recipients(self, recipients: List[Recipient]) -> List[Recipient]:
        return list(filter(lambda r: r.phone_number and len(r.phone_number), self.clean_recipients(recipients)))
