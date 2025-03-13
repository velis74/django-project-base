import datetime

import requests

from rest_framework import status

from django_project_base.country_holidays import holidays_api_url
from tests.test_base import TestBase


class RetrieveHolidaysTest(TestBase):
    def test_retrieve_holidays(self):
        response: requests.Response = requests.get(holidays_api_url % (datetime.datetime.now().year, "SI"), timeout=6)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
