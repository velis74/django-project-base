from unittest import TestCase

from main.models import InternalMail
from main.rest_df.internal_mail.commands.internal_email_command import InternalEmailCommand
from main.rest_df.internal_mail.commands.report_email_duplicates_command import ReportEmailDuplicatesCommand


class TestReportEmailDuplicatesCommandIsinstanceOfInternalMailCommand(TestCase):
    def test_report_email_duplicates_isinstance_of_internal_mail_command(self):
        self.assertTrue(isinstance(ReportEmailDuplicatesCommand(InternalMail()), InternalEmailCommand))
