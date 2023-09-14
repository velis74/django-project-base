import boto3
from django.conf import settings


def get_aws_session():
    return boto3.Session(
        aws_access_key_id=getattr(settings, "AWS_SES_ACCESS_KEY_ID", None),
        aws_secret_access_key=getattr(settings, "AWS_SES_SECRET_ACCESS_KEY", None),
        region_name=getattr(settings, "AWS_SES_REGION_NAME", None),
    )


class AwsSes:
    client = (lambda: get_aws_session().client("ses"))()
