from django.contrib.contenttypes.models import ContentType

from django_project_base.licensing.logic import LogAccessService
from django_project_base.licensing.models import LicenseAccessUse
from django_project_base.notifications.tests.notifications_transaction_test_case import NotificationsTransactionTestCase


class TestRemainingLicense(NotificationsTransactionTestCase):
    def test_remaining_license(self):
        used_amount = 10
        mail = self.create_notification_email_object().send()
        LicenseAccessUse.objects.create(
            type=LicenseAccessUse.UseType.USE,
            user_id=str(self.test_user.pk),
            content_type_object_id=str(mail.pk),
            content_type=ContentType.objects.get_for_model(mail._meta.model),
            amount=-100,
            comment=dict(comment="", count=10, item_price=1, sender=""),
        )
        LicenseAccessUse.objects.create(
            type=LicenseAccessUse.UseType.USE,
            user_id=str(self.test_user.pk),
            content_type_object_id=str(mail.pk),
            content_type=ContentType.objects.get_for_model(mail._meta.model),
            amount=used_amount,
            comment=dict(comment="", count=10, item_price=1, sender=""),
        )
        log_service = LogAccessService()
        usage = log_service.report(user=self.test_user)
        credit = log_service._user_access_user_inflow(self.test_user.pk)
        self.assertEqual(credit - used_amount, usage["remaining_credit"])
