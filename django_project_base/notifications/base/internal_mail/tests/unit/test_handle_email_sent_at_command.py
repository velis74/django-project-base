from django.test import TransactionTestCase

from main.logic.mars_mail_message import MarsMailMessage
from main.models import InternalMail as InternalMailModel
from main.rest_df.internal_mail.commands.handle_email_sent_at_command import HandleEmailSentAtCommand
from main.rest_df.internal_mail.tests.internal_mail_test_mixin import InternalMailTestMixin


class HandleEmailSentAtCommandTest(InternalMailTestMixin, TransactionTestCase):
    databases = ['default', 'message_store_read']

    def test_handle_email_sent_at_command(self):
        mail: MarsMailMessage = self.create_mars_message_object()
        mail.send()
        internal_mail_object: InternalMailModel = InternalMailModel.objects.all().first()
        internal_mail_object.sent_at = None
        internal_mail_object.save(action='save', update_fields=['sent_at'])
        internal_mail_object.refresh_from_db()
        self.assertIsNone(internal_mail_object.sent_at)
        HandleEmailSentAtCommand(internal_mail_object).execute()
        internal_mail_object.refresh_from_db()
        self.assertIsNotNone(internal_mail_object.sent_at)
