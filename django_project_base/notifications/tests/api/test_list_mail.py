import socket

import swapper
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from django_project_base.notifications.email_notification import EMailNotification
from django_project_base.notifications.models import DjangoProjectBaseMessage, DjangoProjectBaseNotification
from django_project_base.notifications.tests.notifications_transaction_test_case import NotificationsTransactionTestCase


class TestListMails(NotificationsTransactionTestCase):
    number_of_emails = 10

    def setUp(self) -> None:
        super().setUp()
        self.mail_data = dict(
            title="test list mail",
            message="test list mail content",
            recipients=[self.test_user.pk],
            sender="support@velis.si",
        )
        for i in range(0, self.number_of_emails):
            EMailNotification(
                message=DjangoProjectBaseMessage(
                    subject=self.mail_data["title"], body=self.mail_data["message"], footer=""
                ),
                raw_recipents=[
                    self.test_user.pk,
                ],
                project=swapper.load_model("django_project_base", "Project").objects.first().slug,
                recipients=[
                    self.test_user.pk,
                ],
                content_entity_context="example_email" "",
            ).send()

    def test_list_internal_mails(self):
        response: Response = self.api_client.get(
            reverse("notification-list"),
            format="json",
            HTTP_HOST=socket.gethostname().lower(),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self._login_to_api_client_with_test_user()
        response: Response = self.api_client.get(
            reverse("notification-list"),
            format="json",
            HTTP_HOST=socket.gethostname().lower(),
            HTTP_CURRENT_PROJECT=swapper.load_model("django_project_base", "Project").objects.first().slug,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))

        self.assertEqual(self.number_of_emails,
                         DjangoProjectBaseNotification.objects.get(pk=response.data[0]["id"]).counter)
