import uuid
from typing import List

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django_project_base.notifications.base.channels.channel import Channel, Recipient
from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.models import DjangoProjectBaseNotification


class MailChannel(Channel):
    id = ChannelIdentifier.MAIL.value

    name = "EMail"

    notification_price = 0.0002  # TODO get from settings

    provider_setting_name = "EMAIL_PROVIDER"

    def send(self, notification: DjangoProjectBaseNotification, extra_data, **kwargs) -> int:
        if getattr(settings, "TESTING", False):
            return super().send(notification=notification, extra_data=extra_data)
        message = self.provider.get_message(notification)
        sender = self.sender(notification)
        self.provider.client_send(
            self.sender(notification),
            Recipient(identifier=str(uuid.uuid4()), phone_number="", email=sender),
            message,
            str(uuid.uuid4()),
        )
        return super().send(notification=notification, extra_data=extra_data)

    def get_recipients(self, notification: DjangoProjectBaseNotification, unique_identifier=""):
        return list(set(super().get_recipients(notification, unique_identifier="email")))

    def clean_email_recipients(self, recipients: List[Recipient]) -> List[Recipient]:
        valid = []
        for email in self.clean_recipients(recipients):
            try:
                validate_email(email.email)
                valid.append(email)
            except ValidationError:
                pass
        return valid
