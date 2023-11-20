from django.conf import settings

from django_project_base.licensing.logic import LogAccessService
from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.tests.notifications_transaction_test_case import NotificationsTransactionTestCase


class TestRemainingLicense(NotificationsTransactionTestCase):
    def test_remaining_license(self):
        mail = self.create_notification_email_object().send()
        log_service = LogAccessService()
        usage = log_service.report(user=self.test_user)
        credit = log_service._user_access_user_inflow(self.test_user.pk)
        channel = ChannelIdentifier.channel(
            mail.required_channels.split(",")[0], ensure_dlr_user=False, settings=settings
        )
        self.assertEqual(credit - channel.notification_price, usage["remaining_credit"])
