from typing import Optional, Union

import boto3

from django.conf import Settings
from rest_framework.status import is_success

from django_project_base.notifications.base.channels.channel import Recipient
from django_project_base.notifications.base.channels.integrations.provider_integration import ProviderIntegration
from django_project_base.notifications.models import DeliveryReport, DjangoProjectBaseNotification


class AwsSnsSingleSMS(ProviderIntegration):
    key_id: str
    access_key: str
    region: str

    def __init__(self) -> None:
        super().__init__(settings=object())

    def ensure_credentials(self, settings: Optional[Settings] = None):
        if settings and getattr(settings, "TESTING", False):
            return
        self.key_id = getattr(settings, "NOTIFICATIONS_AWS_SES_ACCESS_KEY_ID", None)
        self.access_key = getattr(settings, "NOTIFICATIONS_AWS_SES_SECRET_ACCESS_KEY", None)
        self.region = getattr(settings, "NOTIFICATIONS_AWS_SES_REGION_NAME", None)
        self.settings = settings
        assert self.key_id, "AWS SES key id required"
        assert self.access_key, "AWS SES key id access key required"
        assert self.region, "AWS SES region required"

    def _get_sms_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        return super()._get_sms_message(notification)

    def validate_send(self, response: dict):
        assert response
        assert is_success(response.get("ResponseMetadata", {}).get("HTTPStatusCode", 500))

    def client_send(self, sender: str, recipient: Recipient, msg: str, dlr_id: str):
        if not recipient.phone_number:
            return
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
            .publish(PhoneNumber=recipient.phone_number, Message=msg, MessageAttributes=smsattrs)
        )
        self.validate_send(res)

    def get_message(self, notification: DjangoProjectBaseNotification) -> Union[dict, str]:
        return self._get_sms_message(notification)

    def parse_delivery_report(self, dlr: DeliveryReport):
        pass

    @property
    def delivery_report_username_setting_name(self) -> str:
        return "aws-sns-sms-dlr-user"

    @property
    def delivery_report_password_setting_name(self) -> str:
        return "aws-sns-sms-dlr-password"

    def ensure_dlr_user(self, project_slug: str):
        pass

    def enqueue_dlr_request(self, pk: str):
        pass
