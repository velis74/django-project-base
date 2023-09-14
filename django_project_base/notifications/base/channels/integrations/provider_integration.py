from abc import ABC, abstractmethod
from typing import Type, Union

from django_project_base.notifications.base.channels.channel import Channel, Recipient
from django_project_base.notifications.models import DeliveryReport, DjangoProjectBaseNotification


class ProviderIntegration(ABC):
    channel: Type[Channel]
    settings: object

    is_sms_provider = True

    def __init__(self, channel: Type[Channel], settings: object) -> None:
        super().__init__()
        self.channel = channel
        self.settings = settings

    @abstractmethod
    def ensure_credentials(self, extra_data: dict):
        pass

    @abstractmethod
    def client_send(self, sender: str, recipient: Recipient, msg: str, dlr_id: str):
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
        pass
