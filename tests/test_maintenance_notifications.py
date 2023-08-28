import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from django_project_base.notifications.models import DjangoProjectBaseMessage
from django_project_base.utils import get_pk_name
from tests.test_base import TestBase


class TestMaintenanceNotifications(TestBase):
    url = "/maintenance-notification/"

    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def _create_maintenance_notification(self, payload: dict) -> Response:
        self._login_with_test_user_one()
        _payload: dict = {
            "delayed_to": int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()),
            "message": {"body": "Planned maintenance"},
        }
        _payload.update(payload)
        return self.api_client.post(self.url, _payload, format="json")

    def test_create_maintenance_notification(self):
        self.assertEqual(status.HTTP_201_CREATED, self._create_maintenance_notification({}).status_code)
        self.assertEqual(
            self._create_maintenance_notification(dict(delayed_to=datetime.datetime.now())).status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            self._create_maintenance_notification(
                dict(delayed_to=(datetime.datetime.now() - datetime.timedelta(hours=1)).timestamp())
            ).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_list_maintenance_notification(self):
        create_response: Response = self._create_maintenance_notification({})
        self.assertEqual(status.HTTP_201_CREATED, create_response.status_code)
        list_response: Response = self.api_client.get(self.url)
        self.assertEqual(1, len(list_response.data))

        # acknowledge notification - it was read by user
        acknowledged_response: Response = self.api_client.post(
            f"{self.url}acknowledged/",
            {
                get_pk_name(DjangoProjectBaseMessage): list_response.data[0][get_pk_name(DjangoProjectBaseMessage)],
                "acknowledged_identifier": 5,
            },
        )
        self.assertEqual(status.HTTP_201_CREATED, acknowledged_response.status_code)
        self.assertEqual(1, len(self.api_client.get(self.url).data))
