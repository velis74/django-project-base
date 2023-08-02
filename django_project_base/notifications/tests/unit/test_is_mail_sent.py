from django_project_base.notifications.models import DjangoProjectBaseNotification
from django_project_base.notifications.tests.notifications_transaction_test_case import (
    NotificationsTransactionTestCase,
    TestNotificationViaEmail,
)


class IsEmailSentTest(NotificationsTransactionTestCase):
    def test_is_email_sent(self):
        notification: TestNotificationViaEmail = self.create_notification_email_object()
        notification.send()
        notification_db_object: DjangoProjectBaseNotification = DjangoProjectBaseNotification.objects.all().first()
        self.assertEqual(len(notification_db_object.sent_channels.split(",")), 1)
        assert isinstance(notification_db_object.sent_at, int)
        self.assertIsNone(notification_db_object.exceptions)

    # def test_is_email_queued(self):
    #     mail_queue: Queue = QueueFactory("mail")
    #     mail_queue.clear()
    #     send_mail("test", "test", device=None, to_mail=["aa@ff.si"], mail_content_entity_context={})
    #     self.assertEqual(1, mail_queue.length)
