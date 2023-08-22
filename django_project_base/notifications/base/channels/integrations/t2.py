import re

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
from requests.auth import HTTPBasicAuth
from rest_framework import status
from sms_counter import SMSCounter

from django_project_base.celery.settings import NOTIFICATION_QUEABLE_HARD_TIME_LIMIT
from django_project_base.notifications.models import DjangoProjectBaseNotification


class T2:
    sms_from_number: str
    username: str
    password: str

    endpoint_one = "send_sms"
    endpoint_multi = "send_multiple_sms"

    url = ""

    def __init__(self) -> None:
        super().__init__()

    def __ensure_credentials(self, extra_data):
        self.sms_from_number = getattr(settings, "SMS_SENDER", None)
        self.username = getattr(settings, "T2_USERNAME", None)
        self.password = getattr(settings, "T2_PASSWORD", None)
        self.url = getattr(settings, "SMS_API_URL", None)
        if stgs := extra_data.get("SETTINGS"):
            self.sms_from_number = getattr(stgs, "SMS_SENDER", None)
            self.username = getattr(stgs, "T2_USERNAME", None)
            self.password = getattr(stgs, "T2_PASSWORD", None)
            self.url = getattr(stgs, "SMS_API_URL", None)
        assert self.sms_from_number, "SMS_SENDER is required"
        assert self.username, "T2_USERNAME is required"
        assert self.password, "T2_PASSWORD is required"
        assert len(self.url) > 0, "T2_PASSWORD is required"

    def send(self, notification: DjangoProjectBaseNotification, **kwargs):
        self.__ensure_credentials(extra_data=kwargs.get("extra_data"))

        to = (
            [get_user_model().objects.get(pk=u).userprofile.phone_number for u in notification.recipients.split(",")]
            if not notification.recipients_list
            else [u.userprofile.phone_number for u in notification.recipients_list]
        )

        multi = len(to) > 1

        endpoint = self.endpoint_multi if multi else self.endpoint_one

        message = f"{notification.message.subject or ''}"

        if notification.message.subject:
            message += "\n\n"

        message += notification.message.body

        text_only = re.sub("[ \t]+", " ", strip_tags(message))
        # Strip single spaces in the beginning of each line
        message = text_only.replace("\n ", "\n").replace("\n", "\r\n").strip()

        basic_auth = HTTPBasicAuth(self.username, self.password)
        response = requests.post(
            f"{self.url}{endpoint}",
            auth=basic_auth,
            json={
                "from_number": self.sms_from_number,
                f"to_number{'s' if multi else ''}": to if multi else to[0],
                "message": message,
            },
            verify=False,
            headers={"Content-Type": "application/json"},
            timeout=int(0.8 * NOTIFICATION_QUEABLE_HARD_TIME_LIMIT),
        )
        # todo: what is t2 response code 200 or 201
        # todo: handle messages longer than 160 chars - same as on mars???
        if response.status_code != status.HTTP_200_OK:
            import logging

            logger = logging.getLogger("django")
            exc = Exception(f"Failed sms sending for notification {notification.pk}")
            logger.exception(exc)
            raise exc

        response_data = response.json()

        if str(response_data["error_code"]) != "0":
            import logging

            logger = logging.getLogger("django")
            exc = Exception(f"Faild sms sending for notification {notification.pk} \n\n {str(response_data)}")
            logger.exception(exc)
            raise exc
        return SMSCounter.count(message)["messages"]
