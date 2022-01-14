import datetime

import requests
from django.test import TestCase
from rest_framework import status

from django_project_base.country_holidays import holidays_api_url


class RetrieveHolidaysTest(TestCase):

    def test_retieve_holidays(self):
        response: requests.Response = requests.get(
            holidays_api_url % (datetime.datetime.now().year, 'SI'),
            timeout=6
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
