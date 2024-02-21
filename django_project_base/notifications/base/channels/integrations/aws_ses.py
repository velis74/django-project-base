import base64
import re

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Union

import boto3

from django.conf import Settings
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

    def parse_msg_images(self, msg: dict) -> MIMEMultipart:
        mail = MIMEMultipart("mixed")
        mail["Subject"] = msg["Subject"]["Data"]

        # extract embedded images
        pattern = r'<img[^>]*src="(data:image/([^;]+);base64,([^"]+))"[^>]*>'
        content: str = msg["Body"]["Html"]["Data"]
        # make attachements from images and replace
        embedded: List[str, MIMEImage] = []
        for index, (src, type, data) in enumerate(re.findall(pattern, content)):
            img_name = f"image{index + 1}"
            img_temp = MIMEImage(base64.b64decode(data), type)
            img_temp.add_header("Content-ID", f"{img_name}")
            # this looks kinda ugly, but we need all this data to properly deduplicate and write images in
            embedded.append((src, (img_name, img_temp)))

        deduplicated_embedded = dict(embedded).items()

        # deduplicate images, replace and register attachments
        for src, (img_name, img) in deduplicated_embedded:
            content = content.replace(src, f"cid:{img_name}")

        # attach body
        mail.attach(MIMEText(content, "html"))

        # just to make sure, body comes first, then image
        for _, (_, img) in deduplicated_embedded:
            mail.attach(img)

        return mail

    def client_send(self, sender: str, recipient: Recipient, msg: dict, dlr_id: str):
        if not recipient.email:
            return

        msg = self.parse_msg_images(msg)

        res = (
            boto3.Session(
                aws_access_key_id=self.key_id,
                aws_secret_access_key=self.access_key,
                region_name=self.region,
            )
            .client("ses")
            .send_raw_email(
                Source=sender,
                Destinations=[recipient.email],
                RawMessage={"Data": msg.as_string()},
            )
        )
        self.validate_send(res)
