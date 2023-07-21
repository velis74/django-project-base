import copy
import socket

from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from device_simulator.tests.device_simulator_test_mixin import DeviceSimulatorTestMixin
from main.rest_df.internal_mail.internal_mail import InternalMail
from main.rest_api_config.rest_api_config import REST_API_CONFIG


class TestListInternalMails(DeviceSimulatorTestMixin, TransactionTestCase):
    """
    TransactionTestCase is used insted of TestCase due to using 2 db connections. And in test we are
    dont want to isolate data for separate db connections.
    """
    databases = ['default', 'message_store_read']
    number_of_emails = 10

    def setUp(self) -> None:
        super().setUp()
        self.init()
        self.internal_mail_data = dict(
            title='test list mail', message='test list mail content',
            recipients=['klemen.spruk@velis.si', 'admin@velis.si'], sender='support@velis.si'
        )
        for i in range(0, self.number_of_emails):
            InternalMail(**self.internal_mail_data).send()
            altered_data: dict = copy.copy(self.internal_mail_data)
            altered_data['title'] = 'test list mail changed'
            InternalMail(**altered_data).send()

    def test_list_internal_mails(self):
        response: Response = self.api_client.get(
            reverse(REST_API_CONFIG.InternalMail.url_reverse + '-list'),
            format='json',
            HTTP_HOST=socket.gethostname().lower())
        # you have to be admin user to list internal mails
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.upgrade_api_client_user_to_staff()
        response: Response = self.api_client.get(
            reverse(REST_API_CONFIG.InternalMail.url_reverse + '-list'),
            format='json',
            HTTP_HOST=socket.gethostname().lower())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # similar emails are grouped and thus we get 2 objects as result with count of 10
        self.assertEqual(2, len(response.data))
        self.assertEqual(self.number_of_emails, response.data[0]['counter'])
        self.assertEqual(self.number_of_emails, response.data[1]['counter'])
