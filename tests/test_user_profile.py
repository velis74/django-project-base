from django.test import TestCase
from rest_framework.test import APIClient


class TestProfileViewSet(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_get_current_profile(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')

        response = self.api_client.get('/account/profile', {}, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.api_client.get('/account/profile/miha', {}, format='json')
        self.assertEqual(len(response.data), 1)
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
