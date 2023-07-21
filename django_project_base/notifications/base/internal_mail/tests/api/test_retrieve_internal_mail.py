import socket

from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from device_simulator.tests.device_simulator_test_mixin import DeviceSimulatorTestMixin
from main.rest_df.internal_mail.internal_mail import InternalMail
from main.models import InternalMail as InternalMailModel
from main.rest_api_config.rest_api_config import REST_API_CONFIG


class TestRetrieveInternalMail(DeviceSimulatorTestMixin, TransactionTestCase):
    databases = ['default', 'message_store_read']

    def setUp(self) -> None:
        super().setUp()
        self.init()
        self.internal_mail_data = dict(
            title='test retrieve mail', message='test retrieve  mail content',
            recipients=['klemen.spruk@velis.si', 'admin@velis.si'], sender='support@velis.si'
        )
        InternalMail(**self.internal_mail_data).send()

    def test_retrieve_internal_mail(self):
        internal_mail_pk: int = InternalMailModel.objects.all().first().pk
        self.upgrade_api_client_user_to_staff()
        retrieve_response: Response = self.api_client.get(
            reverse(REST_API_CONFIG.InternalMail.url_reverse + '-detail',
                    kwargs=dict(pk=internal_mail_pk)),
            format='json',
            HTTP_HOST=socket.gethostname().lower())
        self.assertEqual(status.HTTP_200_OK, retrieve_response.status_code)
        self.assertEqual(retrieve_response.data.get(InternalMailModel._meta.pk.name), internal_mail_pk)
