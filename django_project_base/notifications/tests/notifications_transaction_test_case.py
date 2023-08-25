import socket
from typing import List, Type

import swapper
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.channels.mail_channel import MailChannel
from django_project_base.notifications.base.notification import Notification
from django_project_base.notifications.models import DjangoProjectBaseMessage


class TestNotificationViaEmail(Notification):
    @property
    def via_channels(self) -> List[Type[Channel]]:
        return [MailChannel]


class NotificationsTransactionTestCase(TransactionTestCase):
    api_client: APIClient

    @property
    def test_user(self):
        return get_user_model().objects.get(username="testuser")

    def setUp(self) -> None:
        super().setUp()
        self.__createUser()
        swapper.load_model("django_project_base", "Project").objects.create(
            name="test", slug="test", owner=self.test_user.userprofile
        )
        self.api_client = APIClient()

    def _login_to_api_client_with_test_user(self):
        user_token, token_created = Token.objects.get_or_create(user=self.test_user)
        self.api_client.credentials(
            HTTP_AUTHORIZATION="Token " + user_token.key, HTTP_HOST=socket.gethostname().lower()
        )

    def __createUser(self):
        get_user_model().objects.get_or_create(
            **dict(
                username="testuser",
                email="testuser@testuser.testuser",
                first_name="testuser",
                last_name="testuser",
            )
        )

    def create_notification_email_object(self) -> TestNotificationViaEmail:
        return TestNotificationViaEmail(
            message=DjangoProjectBaseMessage.objects.create(subject="Test mail", body="content"),
            raw_recipents=[self.test_user.pk],
            project=swapper.load_model("django_project_base", "Project").objects.first().slug,
            recipients=[self.test_user.pk],
            persist=True,
            user=self.test_user,
        )
