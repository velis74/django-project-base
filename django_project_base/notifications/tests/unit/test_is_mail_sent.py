import uuid

from django.conf import settings

from django_project_base.licensing.logic import LogAccessService
from django_project_base.notifications.base.channels.channel import Recipient
from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.base.notification import Notification
from django_project_base.notifications.models import DeliveryReport, DjangoProjectBaseNotification
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

    def test_resend_email(self):
        lic_start = LogAccessService().report(self.test_user)
        notification: DjangoProjectBaseNotification = self.create_notification_email_object().send()
        lic_first_sent = LogAccessService().report(self.test_user)
        self.assertIsNotNone(notification.sent_at)
        self.assertFalse(bool(notification.failed_channels))
        self.assertEqual(notification.required_channels, notification.sent_channels)
        channel = ChannelIdentifier.channel(
            notification.required_channels.split(",")[0], ensure_dlr_user=False, settings=settings
        )
        dlr_pk = str(uuid.uuid4())
        dlr_count = DeliveryReport.objects.all().count()
        resend_data = channel._make_send(
            notification_obj=notification,
            rec_obj=Recipient(identifier=str(self.test_user.pk), phone_number="+38634000000", email="xyz@xyz.xyz"),
            message_str="message",
            dlr_pk=dlr_pk,
        )
        self.assertFalse(resend_data[1])
        self.assertIsNone(resend_data[0])
        self.assertEqual(dlr_count, DeliveryReport.objects.all().count())
        Notification.resend(notification=notification, user_pk=self.test_user.pk)
        self.assertEqual(dlr_count, DeliveryReport.objects.all().count())
        lic_resend = LogAccessService().report(self.test_user)
        self.assertEqual(lic_first_sent["remaining_credit"], lic_resend["remaining_credit"])
        self.assertTrue(lic_start["remaining_credit"] > lic_resend["remaining_credit"])

    # def test_is_email_queued(self):
    #     mail_queue: Queue = QueueFactory("mail")
    #     mail_queue.clear()
    #     send_mail("test", "test", device=None, to_mail=["aa@ff.si"], mail_content_entity_context={})
    #     self.assertEqual(1, mail_queue.length)
