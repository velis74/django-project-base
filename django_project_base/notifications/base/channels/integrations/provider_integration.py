import logging
import re
from abc import ABC, abstractmethod
from typing import Any, List, Type, Union

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.html import strip_tags

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.phone_number_parser import PhoneNumberParser
from django_project_base.notifications.models import DeliveryReport, DjangoProjectBaseNotification


class ProviderIntegration(ABC):
    channel: Type[Channel]
    settings: object

    is_sms_provider = True

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

    def send(self, notification: DjangoProjectBaseNotification, **kwargs) -> int:
        self.ensure_credentials(extra_data=kwargs.get("extra_data"))
        logger = logging.getLogger("django")
        try:
            message = self.get_message(notification)

            recipients = self.get_recipients(notification)

            if not recipients:
                raise ValueError("No valid recipientsc")

            sent_no = 0
            for recipient in recipients:  # noqa: E203
                dlr = self.create_delivery_report(notification)
                try:
                    self.client_send(self.sender(notification), recipient, message, str(dlr.pk))
                    sent_no += 1 if isinstance(recipient, str) else len(recipient)
                except Exception as ge:
                    logger.exception(ge)

            if self.is_sms_provider:
                from django_project_base.notifications.base.channels.integrations.t2 import SMSCounter

                sent_no = sent_no * SMSCounter.count(message)["messages"]
            return sent_no
        except Exception as e:
            logger.exception(e)
            raise e

    @abstractmethod
    def get_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        pass

    @abstractmethod
    def client_send(self, sender: str, recipient: Union[str, List[str]], msg: str, dlr_id: str):
        pass

    @abstractmethod
    def validate_send(self, response: Any):
        pass

    @abstractmethod
    def get_recipients(self, notification: DjangoProjectBaseNotification) -> Union[List[str], List[List[str]]]:
        pass

    @abstractmethod
    def ensure_credentials(self, extra_data: dict):
        pass

    def _get_sms_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        message = f"{notification.message.subject or ''}"

        if notification.message.subject:
            message += "\n\n"

        message += notification.message.body

        text_only = re.sub("[ \t]+", " ", strip_tags(message))
        # Strip single spaces in the beginning of each line
        message = text_only.replace("\n ", "\n").replace("\n", "\r\n").strip()
        return message

    def create_delivery_report(self, notification: DjangoProjectBaseNotification) -> DeliveryReport:
        report = DeliveryReport.objects.create(
            notification=notification,
            user_id=notification.user,
            channel=f"{self.channel.__module__}.{self.channel.__name__}",
            provider=f"{self.__module__}.{self.__class__.__name__}",
        )
        return report

    @abstractmethod
    def parse_delivery_report(self, dlr: DeliveryReport):
        pass
