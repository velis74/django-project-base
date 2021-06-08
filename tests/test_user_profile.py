from django.core.cache import cache
from django.test import TestCase
from example.demo_django_base.models import UserProfile
from rest_framework.test import APIClient


class TestProfileViewSet(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_get_current_profile(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')

        response = self.api_client.get('/account/profile', {}, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.api_client.get('/account/profile/1', {}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_search_url_is_disabled(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')
        response = self.api_client.get('/account/profile/search/miha', {}, format='json')
        self.assertEqual(response.status_code, 404)

    def test_search_query(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')
        response = self.api_client.get('/account/profile?search=mi', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['full_name'], 'Miha Novak')

        response = self.api_client.get('/account/profile?search=j', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['full_name'], 'Janez Novak')

    def test_supperss_is_staff_is_superuser(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')
        response = self.api_client.get('/account/profile/1', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('is_staff', 'not_exist'), 'not_exist')
        self.assertEqual(response.data.get('is_superuser', 'not_exist'), 'not_exist')

        miha = UserProfile.objects.get(username='miha')
        miha.is_staff = True
        miha.is_superuser = True
        miha.save()

        cache.delete('django-user-%d' % miha.id)
        response = self.api_client.get('/account/profile/1', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('is_staff', 'not_exist'), True)
        self.assertEqual(response.data.get('is_superuser', 'not_exist'), True)

        response = self.api_client.get('/account/profile/2', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('is_staff', 'not_exist'), False)
        self.assertEqual(response.data.get('is_superuser', 'not_exist'), False)
