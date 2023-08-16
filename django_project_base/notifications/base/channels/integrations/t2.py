import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from requests.auth import HTTPBasicAuth
from rest_framework import status

from django_project_base.celery.settings import NOTIFICATION_QUEABLE_HARD_TIME_LIMIT
from django_project_base.notifications.models import DjangoProjectBaseNotification


class T2:
    sms_from_number: str
    username: str
    password: str

    endpoint_one = "send_sms"
    endpoint_multi = "send_multiple_sms"

    url = "https://kdjfghs.com/"

    def __init__(self) -> None:
        super().__init__()

    def __ensure_credentials(self, extra_data):
        self.sms_from_number = getattr(settings, "SMS_SENDER", None)
        self.username = getattr(settings, "T2_USERNAME", None)
        self.username = getattr(settings, "T2_PASSWORD", None)
        if stgs := extra_data.get("SETTINGS"):
            self.sms_from_number = getattr(stgs, "SMS_SENDER", None)
            self.username = getattr(stgs, "T2_USERNAME", None)
            self.username = getattr(stgs, "T2_PASSWORD", None)
        assert self.sms_from_number, "SMS_SENDER is required"
        assert self.username, "T2_USERNAME is required"
        assert self.password, "T2_PASSWORD is required"

    def send(self, notification: DjangoProjectBaseNotification, **kwargs):
        self.__ensure_credentials(extra_data=kwargs.get("extra_data"))

        to = (
            [get_user_model().objects.get(pk=u).phone_number for u in notification.recipients.split(",")]
            if not notification.recipients_list
            else notification.recipients_list
        )

        endpoint = self.endpoint_multi if len(to) > 1 else self.endpoint_one

        basic_auth = HTTPBasicAuth(self.username, self.password)
        response = requests.post(
            f"{self.url}{endpoint}",
            auth=basic_auth,
            json={
                "from_number": self.sms_from_number,
                "to_number": to,
                "message": str(notification.message.body),
            },
            verify=False,
            headers={"Content-Type": "application/json"},
            timeout=int(0.8 * NOTIFICATION_QUEABLE_HARD_TIME_LIMIT),
        )
        # todo: what is t2 response code 200 or 201
        if response.status_code != status.HTTP_200_OK:
            import logging

            logger = logging.getLogger("django")
            exc = Exception(f"Faild sms sending for notification {notification.pk}")
            logger.exception(exc)
            raise exc

        respose_data = response.json()

        if str(respose_data.keys()[0]) != "0":
            import logging

            logger = logging.getLogger("django")
            exc = Exception(f"Faild sms sending for notification {notification.pk} \n\n {str(respose_data)}")
            logger.exception(exc)
            raise exc
