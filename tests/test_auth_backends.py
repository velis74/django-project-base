from django.test import TestCase

from example.demo_django_base.models import UserProfile
from rest_framework.test import APIClient


class TestUsersCachingBackend(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_caching_for_bulk_update(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')

        UserProfile.objects.all().update(bio='Just some basic information')

        response = self.api_client.get('/account/profile', {}, format='json')
        self.assertEqual(response.status_code, 200)

        for profile in response.data:
            self.assertEqual(profile['bio'], 'Just some basic information')
