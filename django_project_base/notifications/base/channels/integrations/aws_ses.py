from typing import Union

import boto3
from django.conf import settings
from rest_framework.status import is_success

from django_project_base.notifications.base.channels.channel import Recipient
from django_project_base.notifications.base.channels.integrations.provider_integration import ProviderIntegration
from django_project_base.notifications.models import (
    DeliveryReport,
    DjangoProjectBaseMessage,
    DjangoProjectBaseNotification,
)


class AwsSes(ProviderIntegration):
    key_id: str
    access_key: str
    region: str

    is_sms_provider = False

    def __init__(self) -> None:
        super().__init__(settings=object())

    def validate_send(self, response: dict):
        assert response
        assert is_success(response.get("ResponseMetadata", {}).get("HTTPStatusCode", 500))

    def _get_sms_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        return super()._get_sms_message(notification)

    def ensure_credentials(self, extra_data):
        if settings and getattr(settings, "TESTING", False):
            return
        self.key_id = getattr(settings, "AWS_SES_ACCESS_KEY_ID", None)
        self.access_key = getattr(settings, "AWS_SES_SECRET_ACCESS_KEY", None)
        self.region = getattr(settings, "AWS_SES_REGION_NAME", None)
        self.settings = settings
        if extra_data and (stgs := extra_data.get("SETTINGS")):
            self.settings = stgs
            self.key_id = getattr(stgs, "AWS_SES_ACCESS_KEY_ID", None)
            self.access_key = getattr(stgs, "AWS_SES_SECRET_ACCESS_KEY", None)
            self.region = getattr(stgs, "AWS_SES_REGION_NAME", None)
        assert self.key_id, "AWS SES key id required"
        assert self.access_key, "AWS SES key id access key required"
        assert self.region, "AWS SES region required"

    def get_message(self, notification: DjangoProjectBaseNotification) -> dict:
        msg = {
            "Body": {},
            "Subject": {
                "Charset": "UTF-8",
                "Data": str(notification.message.subject),
            },
        }
        msg["Body"][
            "Html" if notification.message.content_type.lower() == DjangoProjectBaseMessage.HTML else "Text"
        ] = {
            "Charset": "UTF-8",
            "Data": str(notification.message.body),
        }
        return msg

    def parse_delivery_report(self, dlr: DeliveryReport):
        pass

    @property
    def delivery_report_username_setting_name(self) -> str:
        return "aws-ses-email-dlr-user"

    @property
    def delivery_report_password_setting_name(self) -> str:
        return "aws-ses-email-dlr-password"

    def ensure_dlr_user(self, project_slug: str):
        pass

    def enqueue_dlr_request(self, pk: str):
        DeliveryReport.objects.filter(pk=pk).update(status=DeliveryReport.Status.DELIVERED)

    def client_send(self, sender: str, recipient: Recipient, msg: dict, dlr_id: str):
        if not recipient.email:
            return
        res = (
            boto3.Session(
                aws_access_key_id=self.key_id,
                aws_secret_access_key=self.access_key,
                region_name=self.region,
            )
            .client("ses")
            .send_email(
                Destination={
                    "ToAddresses": [recipient.email],
                    "CcAddresses": [],
                    "BccAddresses": [],
                },
                Message=msg,
                Source=sender,
            )
        )
        self.validate_send(res)
