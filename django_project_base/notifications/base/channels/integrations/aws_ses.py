import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth import get_user_model

from django_project_base.notifications.base.channels.integrations.provider_integration import ProviderIntegration
from django_project_base.notifications.models import DjangoProjectBaseMessage, DjangoProjectBaseNotification


class AwsSes(ProviderIntegration):
    key_id: str
    access_key: str
    region: str

    def __init__(self) -> None:
        from django_project_base.notifications.base.channels.mail_channel import MailChannel

        super().__init__(channel=MailChannel, settings=object())

    def __ensure_credentials(self, extra_data):
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

    def send(self, notification: DjangoProjectBaseNotification, **kwargs):
        self.__ensure_credentials(extra_data=kwargs.get("extra_data"))
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

        try:
            sender = self.sender(notification)

            recipients = self.clean_recipients(
                [get_user_model().objects.get(pk=u).email for u in notification.recipients.split(",")]
                if not notification.recipients_list
                else [u["email"] for u in notification.recipients_list if u.get("email")]
            )

            for group in [recipients[i : i + 49] for i in range(0, len(recipients), 49)]:
                boto3.Session(
                    aws_access_key_id=self.key_id,
                    aws_secret_access_key=self.access_key,
                    region_name=self.region,
                ).client("ses").send_email(
                    Destination={
                        "ToAddresses": [sender],
                        "CcAddresses": [],
                        "BccAddresses": group,
                    },
                    Message=msg,
                    Source=sender,
                )
        except ClientError as e:
            import logging

            logger = logging.getLogger("django")
            logger.exception(e)
            raise e
