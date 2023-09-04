import logging
import re
from typing import Union

import boto3
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
from rest_framework.status import is_success

from django_project_base.notifications.base.channels.integrations.provider_integration import ProviderIntegration
from django_project_base.notifications.base.channels.integrations.t2 import SMSCounter
from django_project_base.notifications.models import DjangoProjectBaseNotification


class AwsSnsSingleSMS(ProviderIntegration):
    key_id: str
    access_key: str
    region: str

    def __init__(self) -> None:
        from django_project_base.notifications.base.channels.sms_channel import SmsChannel

        super().__init__(channel=SmsChannel, settings=object())

    def ensure_credentials(self, extra_data):
        self.key_id = getattr(settings, "AWS_SES_ACCESS_KEY_ID", None)
        self.access_key = getattr(settings, "AWS_SES_SECRET_ACCESS_KEY", None)
        self.region = getattr(settings, "AWS_SES_REGION_NAME", None)
        self.settings = settings
        if stgs := extra_data.get("SETTINGS"):
            self.settings = stgs
            self.key_id = getattr(stgs, "AWS_SES_ACCESS_KEY_ID", None)
            self.access_key = getattr(stgs, "AWS_SES_SECRET_ACCESS_KEY", None)
            self.region = getattr(stgs, "AWS_SES_REGION_NAME", None)
        assert self.key_id, "AWS SES key id required"
        assert self.access_key, "AWS SES key id access key required"
        assert self.region, "AWS SES region required"

    def validate_send(self, response: dict):
        assert response
        assert is_success(response.get("ResponseMetadata", {}).get("HTTPStatusCode", 500))

    def get_recipients(self, notification: DjangoProjectBaseNotification):
        return self.clean_sms_recipients(
            [get_user_model().objects.get(pk=u).userprofile.phone_number for u in notification.recipients.split(",")]
            if not notification.recipients_list
            else [u["phone_number"] for u in notification.recipients_list if u.get("phone_number")]
        )

    def client_send(self, sender: str, recipient: str, msg: str):
        smsattrs = {
            "AWS.SNS.SMS.SenderID": {"DataType": "String", "StringValue": sender.replace(" ", "-")},
            "AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Promotional"},
        }

        res = (
            boto3.Session(
                aws_access_key_id=self.key_id,
                aws_secret_access_key=self.access_key,
                region_name=self.region,
            )
            .client("sns")
            .publish(PhoneNumber=recipient, Message=msg, MessageAttributes=smsattrs)
        )
        self.validate_send(res)

    def get_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        return self._get_sms_message(notification)

    def send(self, notification: DjangoProjectBaseNotification, **kwargs):
        self.ensure_credentials(extra_data=kwargs.get("extra_data"))
        logger = logging.getLogger("django")
        try:
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
                    self.client_send(sender, recipient, message)
                    sent_no += 1
                except Exception as ge:
                    logger.exception(ge)
            return SMSCounter.count(message)["messages"] * sent_no
        except Exception as e:
            logger.exception(e)
            raise e
