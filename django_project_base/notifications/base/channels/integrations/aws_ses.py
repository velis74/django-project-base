import boto3
from botocore.exceptions import ClientError
from django.conf import settings


class AwsSes:
    key_id: str
    access_key: str
    region: str

    def __init__(self) -> None:
        super().__init__()
        self.key_id = getattr(settings, "AWS_SES_ACCESS_KEY_ID", None)
        assert self.key_id, "AWS SES key id required"
        self.access_key = getattr(settings, "AWS_SES_SECRET_ACCESS_KEY", None)
        assert self.access_key, "AWS SES key id access key required"
        self.region = getattr(settings, "AWS_SES_REGION_NAME", None)
        assert self.region, "AWS SES region required"

    def send(self, notification: "Notification"):
        msg = {
            "Body": {},
            "Subject": {
                "Charset": "UTF-8",
                "Data": notification.message.subject,
            },
        }
        msg["Body"]["Html" if notification.message.content_subtype.lower() == "html" else "Text"] = {
            "Charset": "UTF-8",
            "Data": notification.message.body,
        }
        from_mail = getattr(settings, "EMAIL_HOST_USER", None)
        assert from_mail, "EMAIL_HOST_USER setting is required"
        try:
            boto3.Session(
                aws_access_key_id=self.key_id,
                aws_secret_access_key=self.access_key,
                region_name=self.region,
                # todo: recipents
            ).client("ses").send_email(
                Destination={"ToAddresses": notification._recipients, "CcAddresses": [], "BccAddresses": []},
                Message=msg,
                Source=from_mail,
            )
        except ClientError as e:
            import logging

            logger = logging.getLogger("django")
            logger.exception(e)
            raise e
