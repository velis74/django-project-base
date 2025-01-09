import base64
import os
import re

from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from typing import Optional, Union

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
        msg["Attachments"] = notification.message.get_attachments()
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
        # Create root multipart/related message
        mail = MIMEMultipart("related")
        mail["Subject"] = msg["Subject"]["Data"]

        # Extract embedded images
        content: str = msg["Body"]["Html"]["Data"]

        pattern_clean = r'<img([^>]*?)(?:width|height)=["\']\d+["\']([^>]*?)>'
        while re.search(pattern_clean, content):
            content = re.sub(pattern_clean, r"<img\1\2>", content)

        # Process each image
        all_images = []
        pattern = r'<img[^>]*src="(data:image/([^;]+);base64,([^"]+))"[^>]*>'
        for index, (src, img_type, data) in enumerate(re.findall(pattern, content)):
            # Generate unique content ID
            content_id = make_msgid()  # This creates a unique ID like <123.ABC@domain>

            # Create image part
            img = MIMEImage(base64.b64decode(data), _subtype=img_type.lower())
            img.add_header("Content-ID", content_id)
            img.add_header("Content-Disposition", "inline")

            # Replace data URI with cid: URI in HTML
            content = content.replace(src, f"cid:{content_id[1:-1]}")  # Remove < > from content ID

            # Attach image part
            all_images.append(img)

        # Update HTML content with cid: references
        html_part = MIMEText(content, "html")
        mail.attach(html_part)
        for img in all_images:
            mail.attach(img)

        for attachment in msg.get("Attachments", []):
            with open(attachment.file.path, "rb") as f:
                part = MIMEApplication(f.read())
                part.add_header("Content-Disposition", "attachment", filename=os.path.basename(attachment.file.name))
                mail.attach(part)

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
