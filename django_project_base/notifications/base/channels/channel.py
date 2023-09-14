import logging
import re
from abc import ABC, abstractmethod
from typing import List, Optional, Union, Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
from django.utils.module_loading import import_string
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django_project_base.notifications.base.channels.integrations.provider_integration import ProviderIntegration
from django_project_base.notifications.base.phone_number_parser import PhoneNumberParser
from django_project_base.notifications.models import DjangoProjectBaseNotification, DeliveryReport
from django_project_base.utils import get_pk_name


class Recipient:
    identifier: str
    phone_number: str
    email: str
    unique_attribute: str

    def __init__(self, identifier: str, phone_number: str, email: str, unique_attribute: str = "identifier") -> None:
        super().__init__()
        assert identifier
        assert phone_number
        assert email
        self.identifier = identifier
        self.phone_number = phone_number
        self.email = email
        self.unique_attribute = unique_attribute

    def __eq__(self, __o: "Recipient") -> bool:
        return str(getattr(self, self.unique_attribute)) == str(getattr(__o, self.unique_attribute))

    def __hash__(self) -> int:
        return getattr(self, self.unique_attribute).__hash__()


class Channel(ABC):
    id = None

    name = ""

    notification_price = 0

    provider_setting_name = ""

    _provider: ProviderIntegration

    def _get_provider(self):
        return self._provider

    def _set_provider(self, val: ProviderIntegration):
        self._provider = val

    provider = property(_get_provider, _set_provider)

    def sender(self, notification: DjangoProjectBaseNotification) -> str:
        _sender = getattr(notification, "sender", {}).get(self.name)
        assert _sender, "Notification sender is required"
        return _sender

    def set_provider(self, extra_settings: Optional[dict], setting_name: str):
        def get_first_provider(val: Union[str, List]):
            if val and isinstance(val, list):
                self.provider = import_string(val[0])()
                return

            self.provider = import_string(val)()

        if extra_settings and getattr(extra_settings.get("SETTINGS", object()), setting_name, None):
            get_first_provider(getattr(extra_settings["SETTINGS"], setting_name))
            return
        get_first_provider(getattr(settings, setting_name, ""))

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

    def _get_sms_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        message = f"{notification.message.subject or ''}"

        if notification.message.subject:
            message += "\n\n"

        message += notification.message.body

        text_only = re.sub("[ \t]+", " ", strip_tags(message))
        # Strip single spaces in the beginning of each line
        message = text_only.replace("\n ", "\n").replace("\n", "\r\n").strip()
        return message

    def create_delivery_report(
        self, notification: DjangoProjectBaseNotification, recipient: Union[Recipient, List[Recipient]]
    ) -> DeliveryReport:
        recs = recipient if isinstance(recipient, list) else [recipient]
        for user in recs:
            report = DeliveryReport.objects.create(
                notification=notification,
                user_id=user.identifier,
                channel=f"{self.__module__}.{self.__name__}",
                provider=f"{self.__module__}.{self.__class__.__name__}",
            )
            return report

    @abstractmethod
    def validate_send(self, response: Any):
        pass

    @abstractmethod
    def get_recipients(self, notification: DjangoProjectBaseNotification, unique_identifier="email") -> List[Recipient]:
        rec_obj = notification.recipients_list
        if not rec_obj:
            att = ("email", "phone_number", get_pk_name(get_user_model()))
            rec_obj = [
                {k: v for k, v in profile.__dict__.items() if not k.startswith("_") and k in att}
                for profile in [
                    get_user_model().objects.get(pk=u).userprofile for u in notification.recipients.split(",")
                ]
            ]
        return [
            Recipient(
                identifier=u["id"], email=u["email"], phone_number=u["phone_number"], unique_attribute=unique_identifier
            )
            for u in rec_obj
        ]

    def send(self, notification: DjangoProjectBaseNotification, extra_data, **kwargs) -> int:
        self.set_provider(extra_settings=extra_data, setting_name=self.provider_setting_name)
        self.provider.ensure_credentials(extra_data=kwargs.get("extra_data"))
        logger = logging.getLogger("django")
        try:
            message = self.provider.get_message(notification)

            recipients = self.get_recipients(notification)

            if not recipients:
                raise ValueError("No valid recipients")

            sent_no = 0
            for recipient in recipients:  # noqa: E203
                dlr = self.create_delivery_report(notification, recipient)
                try:
                    self.provider.client_send(self.sender(notification), recipient, message, str(dlr.pk))
                    sent_no += 1
                except Exception as ge:
                    logger.exception(ge)

            if self.provider.is_sms_provider:
                from django_project_base.notifications.base.channels.integrations.t2 import SMSCounter

                sent_no = sent_no * SMSCounter.count(message)["messages"]
            return sent_no
        except Exception as e:
            logger.exception(e)
            raise e
