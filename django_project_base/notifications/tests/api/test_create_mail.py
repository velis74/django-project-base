import swapper

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
                project=swapper.load_model("django_project_base", "Project").objects.first(),
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
                project=swapper.load_model("django_project_base", "Project").objects.first(),
                recipients=[
                    self.test_user.pk,
                ],
                persist=False,
            ).send()
        )
        self.assertEqual(DjangoProjectBaseNotification.objects.all().count(), 1)
