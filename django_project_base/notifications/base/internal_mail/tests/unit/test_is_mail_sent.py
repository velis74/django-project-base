import datetime

from django.test import TransactionTestCase

from background_tasks.queues.queue import Queue, QueueFactory
from main.logic.mars_mail_message import MarsMailMessage
from main.mail import send_mail
from main.models import InternalMail
from main.rest_df.internal_mail.tests.internal_mail_test_mixin import InternalMailTestMixin


class IsEmailSentTest(InternalMailTestMixin, TransactionTestCase):
    databases = ['default', 'message_store_read']

    def test_is_email_sent(self):
        mail: MarsMailMessage = self.create_mars_message_object()
        self.assertEqual(mail.send(), len(mail.recipients()))
        internal_mail_object = InternalMail.objects.all().first()
        assert isinstance(internal_mail_object.sent_at, datetime.datetime)
        self.assertIsNone(internal_mail_object.mail_server_exception)

    def test_is_email_queued(self):
        mail_queue: Queue = QueueFactory('mail')
        mail_queue.clear()
        send_mail('test', 'test', device=None, to_mail=['aa@ff.si'], mail_content_entity_context={})
        self.assertEqual(1, mail_queue.length)
