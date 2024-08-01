import socket

import swapper
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from django_project_base.notifications.tests.notifications_transaction_test_case import (
    NotificationsTransactionTestCase,
    TestNotificationViaEmail,
)
from django_project_base.utils import get_pk_name


class TestRetrieveMail(NotificationsTransactionTestCase):
    def test_retrieve_mail(self):
        mail: TestNotificationViaEmail = self.create_notification_email_object()
        notification = mail.send()
        response: Response = self.api_client.get(
            reverse("notification-detail", kwargs=dict(pk=notification.pk)),
            format="json",
            HTTP_HOST=socket.gethostname().lower(),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self._login_to_api_client_with_test_user()
        response: Response = self.api_client.get(
            reverse("notification-detail", kwargs=dict(pk=notification.pk)),
            format="json",
            HTTP_HOST=socket.gethostname().lower(),
            HTTP_CURRENT_PROJECT=swapper.load_model("django_project_base", "Project").objects.first().slug,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        self.assertIsNotNone(response.data[get_pk_name(notification)], str(notification.pk))
        notification.refresh_from_db()
        self.assertEqual(1, notification.counter)
