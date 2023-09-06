from typing import Union

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.status import is_success

from django_project_base.notifications.base.channels.integrations.provider_integration import ProviderIntegration
from django_project_base.notifications.base.phone_number_parser import PhoneNumberParser
from django_project_base.notifications.models import DeliveryReport, DjangoProjectBaseNotification


class NexmoSMS(ProviderIntegration):
    api_key: str
    api_secret: str

    def __init__(self) -> None:
        from django_project_base.notifications.base.channels.sms_channel import SmsChannel

        super().__init__(channel=SmsChannel, settings=object())

    def ensure_credentials(self, extra_data):
        self.api_key = getattr(settings, "NEXMO_API_KEY", None)
        self.api_secret = getattr(settings, "NEXMO_API_SECRET", None)
        self.settings = settings
        if stgs := extra_data.get("SETTINGS"):
            self.settings = stgs
            self.api_key = getattr(stgs, "NEXMO_API_KEY", None)
            self.api_secret = getattr(stgs, "NEXMO_API_SECRET", None)
        assert self.api_key, "NEXMO_API_KEY required"
        assert self.api_secret, "NEXMO_API_SECRET required"

    def validate_send(self, response: object):
        assert response
        assert is_success(response.status_code)

    def client_send(self, sender: str, recipient: str, msg: str, dlr_id: str):
        params: dict = {
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "from": sender,
            "to": recipient,
            "text": msg,
        }
        response = requests.get(
            "https://rest.nexmo.com/sms/json",
            params=params,
            verify=False,
            timeout=4,
        )
        self.validate_send(response)

    def get_recipients(self, notification: DjangoProjectBaseNotification):
        # TODO: SLOVENIA????????
        return PhoneNumberParser.ensure_country_code_slovenia(
            self.clean_recipients(
                [
                    get_user_model().objects.get(pk=u).userprofile.phone_number
                    for u in notification.recipients.split(",")
                ]
                if not notification.recipients_list
                else [u["phone_number"] for u in notification.recipients_list if u.get("phone_number")]
            )
        )

    def get_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        return self._get_sms_message(notification)

    def parse_delivery_report(self, dlr: DeliveryReport):
        pass
