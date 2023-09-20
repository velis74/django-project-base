import re
from abc import ABC, abstractmethod
from typing import Union

import swapper
from django.utils.html import strip_tags

from django_project_base.constants import SEND_NOTIFICATION_SMS
from django_project_base.notifications.models import DeliveryReport, DjangoProjectBaseNotification


class ProviderIntegration(ABC):
    settings: object

    is_sms_provider = True

    def __init__(self, settings: object) -> None:
        super().__init__()
        self.settings = settings

    @abstractmethod
    def validate_send(self, response: dict):
        pass

    @abstractmethod
    def ensure_credentials(self, extra_data: dict):
        pass

    @abstractmethod
    def client_send(self, sender: str, recipient: "Recipient", msg: str, dlr_id: str):  # noqa: F821
        pass

    @property
    @abstractmethod
    def delivery_report_username_setting_name(self) -> str:
        pass

    @property
    @abstractmethod
    def delivery_report_password_setting_name(self) -> str:
        pass

    @abstractmethod
    def parse_delivery_report(self, dlr: DeliveryReport):
        pass

    @abstractmethod
    def ensure_dlr_user(self, project_slug: str):
        pass

    @abstractmethod
    def enqueue_dlr_request(self):
        pass

    @abstractmethod
    def get_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        return ""

    def get_send_notification_sms_text(self, notification: DjangoProjectBaseNotification, host_url: str) -> str:
        if notification.send_notification_sms:
            template: str = swapper.load_model("django_project_base", "ProjectSettings").objects.get(
                name=SEND_NOTIFICATION_SMS, project__slug=notification.project_slug).python_value
            return template.replace("__LINK__", f"{host_url}notification/{str(notification.pk)}/info{'/' if getattr(self.settings, 'APPEND_SLASH', False) else ''}")
        return ""

    @abstractmethod
    def _get_sms_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:

        if notification.send_notification_sms:
            return notification.send_notification_sms_text

        message = f"{notification.message.subject or ''}"

        if notification.message.subject:
            message += "\n\n"

        message += notification.message.body

        text_only = re.sub("[ \t]+", " ", strip_tags(message))
        # Strip single spaces in the beginning of each line
        message = text_only.replace("\n ", "\n").replace("\n", "\r\n").strip()
        return message
