from typing import List

import boto3

from django.conf import settings
from rest_framework import status


def get_aws_session():
    if settings.TESTING:

        class FakeSession:
            client = lambda t, i: object()  # noqa: E731

        return FakeSession()
    return boto3.Session(
        aws_access_key_id=getattr(settings, "NOTIFICATIONS_AWS_SES_ACCESS_KEY_ID", None),
        aws_secret_access_key=getattr(settings, "NOTIFICATIONS_AWS_SES_SECRET_ACCESS_KEY", None),
        region_name=getattr(settings, "NOTIFICATIONS_AWS_SES_REGION_NAME", None),
    )


class AwsSes:
    client = (lambda: get_aws_session().client("ses"))()

    @staticmethod
    def list_sender_emails() -> List[str]:
        return AwsSes.client.list_identities()["Identities"]

    @staticmethod
    def list_verified_sender_emails() -> List[str]:
        return AwsSes.client.list_verified_email_addresses()["VerifiedEmailAddresses"]

    @staticmethod
    def remove_sender_email(email: str):
        if email in AwsSes.list_sender_emails():
            # TODO: EACH DEPLOYMENT SHOULD HAVE ITS OWN AWS ACCOUNT FOR THIS TO BE ENABLED
            # TODO: ALSO DEV MACHINES SHOULD HAVE ITS OWN ACCOUNT
            pass
            # assert (
            #     AwsSes.client.delete_identity(
            #         Identity=email,
            #     )[
            #         "ResponseMetadata"
            #     ]["HTTPStatusCode"]
            #     == status.HTTP_200_OK
            # )

    @staticmethod
    def add_sender_email(email: str):
        if email not in AwsSes.list_sender_emails():
            assert (
                AwsSes.client.verify_email_identity(EmailAddress=email)["ResponseMetadata"]["HTTPStatusCode"]
                == status.HTTP_200_OK
            )
