import copy
from datetime import datetime, timedelta

from django.test import TransactionTestCase

from main.logic.mars_mail_message import MarsMailMessage
from main.models import InternalMail
from main.rest_df.internal_mail.commands.report_email_duplicates_command import ReportEmailDuplicatesCommand
from main.rest_df.internal_mail.config import INTERNAL_MAIL_CHECKING_REPORT_INTERVALS_IN_MINUTES
from main.rest_df.internal_mail.tests.internal_mail_test_mixin import InternalMailTestMixin


class IsReportSentTest(InternalMailTestMixin, TransactionTestCase):
    databases = ['default', 'message_store_read']

    def __test_report_send(self, interval: int, internal_mail_object: InternalMail):
        interval_ago_time: datetime = internal_mail_object.created_at - timedelta(minutes=interval + 1)
        internal_mail_object.counter_updated_at = interval_ago_time
        internal_mail_object.save(action='save', update_fields=['counter_updated_at'])
        internal_mail_object.refresh_from_db()
        ReportEmailDuplicatesCommand(internal_mail_object).execute()
        internal_mail_object.refresh_from_db()

    def test_is_report_sent(self):
        mail: MarsMailMessage = self.create_mars_message_object()
        self.assertEqual(mail.send(), len(mail.recipients()))
        mail.send()
        internal_mail_object = InternalMail.objects.all().first()
        self.assertEqual(2, internal_mail_object.counter)
        intervals: list = copy.copy(INTERNAL_MAIL_CHECKING_REPORT_INTERVALS_IN_MINUTES)
        intervals.sort()
        for time_limit in intervals:
            self.__test_report_send(time_limit, internal_mail_object)
        self.assertEqual(internal_mail_object.reports.all().count(), len(intervals))
