from copy import copy

from django.test import TransactionTestCase

from main.rest_df.internal_mail.internal_mail import InternalMail
from main.models import InternalMail as InternalMailModel


class TestCreateInternalMail(TransactionTestCase):
    databases = ['default', 'message_store_read']

    def setUp(self) -> None:
        super().setUp()
        self.internal_mail_data = dict(
            title='test mail', message='test mail content',
            recipients=['klemen.spruk@velis.si', 'admin@velis.si'], sender='support@velis.si'
        )

    def test_validate_internal_mail(self):
        for attribute in ('title', 'message', 'recipients', 'sender'):
            mail_data: dict = copy(self.internal_mail_data)
            mail_data[attribute] = None
            with self.assertRaises(AssertionError):
                InternalMail(**mail_data)

    def test_create_internal_mail(self):
        mail: InternalMail = InternalMail(**self.internal_mail_data)
        mail.send()
        InternalMailModel.objects.using('message_store_read').get(**self.internal_mail_data)
