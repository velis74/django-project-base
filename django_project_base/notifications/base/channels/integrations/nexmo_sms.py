import logging
import re

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
from rest_framework.status import is_success

from django_project_base.notifications.base.channels.integrations.provider_integration import ProviderIntegration
from django_project_base.notifications.base.channels.integrations.t2 import SMSCounter
from django_project_base.notifications.models import DjangoProjectBaseNotification


class NexmoSMS(ProviderIntegration):
    api_key: str
    api_secret: str

    def __init__(self) -> None:
        from django_project_base.notifications.base.channels.sms_channel import SmsChannel

        super().__init__(channel=SmsChannel, settings=object())

    def __ensure_credentials(self, extra_data):
        self.api_key = getattr(settings, "NEXMO_API_KEY", None)
        self.api_secret = getattr(settings, "NEXMO_API_SECRET", None)
        self.settings = settings
        if stgs := extra_data.get("SETTINGS"):
            self.settings = stgs
            self.api_key = getattr(stgs, "NEXMO_API_KEY", None)
            self.api_secret = getattr(stgs, "NEXMO_API_SECRET", None)
        assert self.api_key, "NEXMO_API_KEY required"
        assert self.api_secret, "NEXMO_API_SECRET required"

    def _client_send(self, sender: str, recipient: str, msg: str):
        params: dict = {
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "from": sender,
            "to": recipient,
            "text": msg,
        }
        return requests.get(
            "https://rest.nexmo.com/sms/json",
            params=params,
            verify=False,
            timeout=4,
        )

    def send(self, notification: DjangoProjectBaseNotification, **kwargs):
        logger = logging.getLogger("django")
        self.__ensure_credentials(extra_data=kwargs.get("extra_data"))
        try:
            message = f"{notification.message.subject or ''}"

            if notification.message.subject:
                message += "\n\n"

            message += notification.message.body

            text_only = re.sub("[ \t]+", " ", strip_tags(message))
            # Strip single spaces in the beginning of each line
            message = text_only.replace("\n ", "\n").replace("\n", "\r\n").strip()
            sender = self.sender(notification)

            recipients = self.clean_sms_recipients(
                [
                    get_user_model().objects.get(pk=u).userprofile.phone_number
                    for u in notification.recipients.split(",")
                ]
                if not notification.recipients_list
                else [u["phone_number"] for u in notification.recipients_list if u.get("phone_number")]
            )

            if not recipients:
                raise ValueError("No valid phone numbers")

            sent_no = 0
            for recipient in recipients:  # noqa: E203
                try:
                    response = self._client_send(sender, recipient, message)
                    assert is_success(response.status_code)
                    sent_no += 1
                except Exception as ge:
                    logger.exception(ge)
            return SMSCounter.count(message)["messages"] * sent_no
        except Exception as e:
            logger.exception(e)
            raise e
