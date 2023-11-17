import socket

import swapper
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from django_project_base.notifications.base.channels.mail_channel import MailChannel
from django_project_base.notifications.email_notification import EMailNotification
from django_project_base.notifications.models import DjangoProjectBaseMessage, DjangoProjectBaseNotification
from django_project_base.notifications.tests.notifications_transaction_test_case import NotificationsTransactionTestCase


class TestCreateMail(NotificationsTransactionTestCase):
    def test_send_mail(self):
        self.assertIsNotNone(
            EMailNotification(
                message=DjangoProjectBaseMessage(subject="test", body="", footer=""),
                raw_recipents=[
                    self.test_user.pk,
                ],
                project=swapper.load_model("django_project_base", "Project").objects.first().slug,
                recipients=[
                    self.test_user.pk,
                ],
            ).send()
        )
        self.assertEqual(DjangoProjectBaseNotification.objects.all().count(), 1)
        self.assertIsNotNone(
            EMailNotification(
                message=DjangoProjectBaseMessage(subject="test", body="", footer=""),
                raw_recipents=[
                    self.test_user.pk,
                ],
                project=swapper.load_model("django_project_base", "Project").objects.first().slug,
                recipients=[
                    self.test_user.pk,
                ],
                persist=False,
            ).send()
        )
        self.assertEqual(DjangoProjectBaseNotification.objects.all().count(), 1)

    def test_api_create_mail(self):
        self._login_to_api_client_with_test_user()
        response: Response = self.api_client.put(
            reverse("notification-detail", kwargs=dict(pk="new")),
            format="json",
            data={
                "message_body": "demo",
                "message_subject": "demo",
                "message_to": [self.test_user.pk],
                "send_on_channels": [MailChannel.name],
            },
            HTTP_HOST=socket.gethostname().lower(),
            HTTP_CURRENT_PROJECT=swapper.load_model("django_project_base", "Project").objects.first().slug,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
