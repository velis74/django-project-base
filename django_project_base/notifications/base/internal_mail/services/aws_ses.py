import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from main.logic.mars_mail_message import MarsMailMessage


class AwsSesService:

    def send(self, email: MarsMailMessage):

        msg = {
            "Body": {},
            "Subject": {
                "Charset": "UTF-8",
                "Data": email.subject,
            },
        }
        msg["Body"]["Html" if email.content_subtype.lower() == "html" else "Text"] = {
            "Charset": "UTF-8",
            "Data": email.body,
        }
        try:
            boto3.Session(
                aws_access_key_id=settings.AWS_SES_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SES_SECRET_ACCESS_KEY,
                region_name=settings.AWS_SES_REGION_NAME,
            ).client("ses").send_email(
                Destination={
                    "ToAddresses": email.recipients(),
                    'CcAddresses': email.cc,
                    'BccAddresses': email.bcc
                },
                Message=msg,
                Source=settings.EMAIL_HOST_USER,
            )
        except ClientError as e:
            import logging
            logger = logging.getLogger('django')
            logger.exception(f"{str(e)} {str(email)} {str(email.recipients())}")
            raise e
