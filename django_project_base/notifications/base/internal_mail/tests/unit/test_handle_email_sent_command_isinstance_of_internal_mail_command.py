from unittest import TestCase

from main.models import InternalMail
from main.rest_df.internal_mail.commands.handle_email_sent_at_command import HandleEmailSentAtCommand
from main.rest_df.internal_mail.commands.internal_email_command import InternalEmailCommand


class TestReportEmailDuplicatesCommandIsinstanceOfInternalMailCommand(TestCase):
    def test_report_email_duplicates_isinstance_of_internal_mail_command(self):
        self.assertTrue(isinstance(HandleEmailSentAtCommand(InternalMail()), InternalEmailCommand))
