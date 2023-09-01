from typing import List, Type

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.phone_number_parser import PhoneNumberParser
from django_project_base.notifications.models import DjangoProjectBaseNotification


class ProviderIntegration:
    channel: Type[Channel]
    settings: object

    def __init__(self, channel: Type[Channel], settings: object) -> None:
        super().__init__()
        self.channel = channel
        self.settings = settings

    def sender(self, notification: DjangoProjectBaseNotification) -> str:
        _sender = getattr(notification, "sender", {}).get(self.channel.name)
        assert _sender, "Notification sender is required"
        return _sender

    def clean_recipients(self, recipients: List[str]) -> List[str]:
        return list(set([r for r in recipients if r not in ("", "None", None)]))

    def clean_email_recipients(self, recipients: List[str]) -> List[str]:
        valid = []
        for email in self.clean_recipients(recipients):
            try:
                validate_email(email)
                valid.append(email)
            except ValidationError:
                pass
        return valid

    def clean_sms_recipients(self, recipients: List[str]) -> List[str]:
        return PhoneNumberParser.valid_phone_numbers(self.clean_recipients(recipients))
