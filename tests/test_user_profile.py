from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from example.demo_django_base.models import UserProfile


class TestProfileViewSet(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_get_current_profile(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')

        response = self.api_client.get('/account/profile', {}, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.api_client.get('/account/profile/1', {}, format='json')
        self.assertEqual(response.data['full_name'], 'Miha Novak')
        self.assertEqual(response.status_code, 200)

    def test_insert_profile(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')
        profile = {"password": "string",
                   "last_login": "2021-06-02T08:49:13.618Z",
                   "is_superuser": False,
                   "username": "string",
                   "first_name": "string",
                   "last_name": "string",
                   "email": "user@example.com",
                   "is_staff": False,
                   "is_active": True,
                   "date_joined": "2021-06-02T08:49:13.618Z",
                   "bio": "string",
                   "phone_number": "string",
                   "language": "string",
                   "theme": "string",
                   "avatar": "string",
                   "reverse_full_name_order": False,
                   "groups": None,
                   "user_permissions": None
                   },
        response = self.api_client.post('/account/profile', profile, format='json')
        self.assertEqual(response.status_code, 500)

    def test_update_profile(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')
        response = self.api_client.patch('/account/profile/1', {'bio': 'Sample bio text.'}, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.api_client.get('/account/profile/1', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('bio', False), 'Sample bio text.')

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

        # we cannot query other users if we are not admins
        response = self.api_client.get('/account/profile?search=j', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        miha = UserProfile.objects.get(username='miha')
        miha.is_staff = True
        miha.save()
        cache.delete('django-user-%d' % miha.id)

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

    def test_profile_destroy(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')
        response = self.api_client.delete('/account/profile/1', {}, format='json')
        self.assertEqual(response.status_code, 403)
        expected_response = b'{"detail":"You do not have permission to perform this action."}'
        self.assertEqual(response.content, expected_response)

        miha = UserProfile.objects.get(username='miha')
        miha.is_staff = True
        miha.is_superuser = True
        miha.save()
        cache.delete('django-user-%d' % miha.id)

        response = self.api_client.delete('/account/profile/2', {}, format='json')
        self.assertEqual(response.status_code, 204)

    def test_profile_destroy_my_profile(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')
        response = self.api_client.get('/account/profile/current', {}, format='json')
        self.assertEqual(response.status_code, 200)
        response = self.api_client.delete('/account/profile/current', {}, format='json')
        self.assertEqual(response.status_code, 204)
        response = self.api_client.get('/account/profile/current', {}, format='json')
        self.assertEqual(response.status_code, 403)
