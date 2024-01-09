from typing import Optional, Union

import requests

from django.conf import Settings
from rest_framework.status import is_success

from django_project_base.notifications.base.channels.channel import Recipient
from django_project_base.notifications.base.channels.integrations.provider_integration import ProviderIntegration
from django_project_base.notifications.base.phone_number_parser import PhoneNumberParser
from django_project_base.notifications.models import DeliveryReport, DjangoProjectBaseNotification


class NexmoSMS(ProviderIntegration):
    api_key: str
    api_secret: str

    def __init__(self) -> None:
        super().__init__(settings=object())

    def ensure_credentials(self, settings: Optional[Settings] = None):
        if settings and getattr(settings, "TESTING", False):
            return
        self.api_key = getattr(settings, "NOTIFICATIONS_NEXMO_API_KEY", None)
        self.api_secret = getattr(settings, "NOTIFICATIONS_NEXMO_API_SECRET", None)
        self.settings = settings
        assert self.api_key, "NOTIFICATIONS_NEXMO_API_KEY required"
        assert self.api_secret, "NOTIFICATIONS_NEXMO_API_SECRET required"

    def _get_sms_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        return super()._get_sms_message(notification)

    def validate_send(self, response: object):
        assert response
        assert is_success(response.status_code)

    def client_send(self, sender: str, recipient: Recipient, msg: str, dlr_id: str):
        # TODO: SLOVENIA????????
        rec = PhoneNumberParser.ensure_country_code_slovenia([recipient.phone_number])
        if not rec:
            return

        if not rec[0]:
            return

        params: dict = {
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "from": sender,
            "to": rec[0],
            "text": msg,
        }
        response = requests.get(
            "https://rest.nexmo.com/sms/json",
            params=params,
            verify=False,
            timeout=4,
        )
        self.validate_send(response)

    def get_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        return self._get_sms_message(notification)

    def parse_delivery_report(self, dlr: DeliveryReport):
        pass

    @property
    def delivery_report_username_setting_name(self) -> str:
        return "nexmo-sms-dlr-user"

    @property
    def delivery_report_password_setting_name(self) -> str:
        return "nexmo-sms-dlr-password"

    def ensure_dlr_user(self, project_slug: str):
        pass

    def enqueue_dlr_request(self, pk: str):
        pass
