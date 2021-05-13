from django.core.cache import cache
from django.test import TestCase
from django_project_base.settings import DJANGO_USER_CACHE
from example.demo_django_base.models import UserProfile
from rest_framework.test import APIClient


class TestUsersCachingBackend(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_caching_for_bulk_update(self):
        self.assertTrue(self.api_client.login(username='miha', password='mihamiha'), 'Not logged in')

        # Try to do something only superuser can
        response = self.api_client.post('/account/impersonate/start', {'username': 'janez'}, format='json')
        self.assertEqual(response.status_code, 403)

        UserProfile.objects.filter(username__in=['miha', 'janez']).update(is_superuser=True, is_staff=True)

        # I still shouldn't be able to do superuser stuff
        response = self.api_client.post('/account/impersonate/start', {'username': 'janez'}, format='json')
        self.assertEqual(response.status_code, 403)

        # Clearing cache, now Miha can do better stuff
        staff = UserProfile.objects.filter(is_staff=True)
        for user in staff:
            cache.delete(DJANGO_USER_CACHE % user.id)

        response = self.api_client.post('/account/impersonate/start', {'username': 'janez'}, format='json')
        self.assertEqual(response.status_code, 200)
