from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from example.demo_django_base.models import Project, UserProfile


class TestProject(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_construction(self):
        assert Project()


class TestProfile(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_construction(self):
        assert UserProfile()

    def test_reverse_full_name_order(self):
        self.assertTrue(self.api_client.login(username='janez', password='janezjanez'), 'Not logged in')
        response = self.api_client.get('/account/profile/current', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['full_name'], 'Janez Novak')

        settings.PROFILE_REVERSE_FULL_NAME_ORDER = True
        response = self.api_client.get('/account/profile/current', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['full_name'], 'Novak Janez')

        settings.PROFILE_REVERSE_FULL_NAME_ORDER = False
        janez = UserProfile.objects.get(username='janez')
        janez.reverse_full_name_order = True
        janez.save()
        response = self.api_client.get('/account/profile/current', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['full_name'], 'Novak Janez')
