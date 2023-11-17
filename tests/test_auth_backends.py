from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient

from django_project_base.settings import USER_CACHE_KEY
from example.demo_django_base.models import UserProfile
from tests.test_base import TestBase


class TestUsersCachingBackend(TestBase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_caching_for_bulk_update(self):
        self.assertTrue(self.api_client.login(username="miha", password="mihamiha"), "Not logged in")

        # Try to do something only superuser can
        response = self.api_client.put("/account/impersonate", {"username": "janez"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertIsNotNone(cache.get(USER_CACHE_KEY.format(id=1)))

        UserProfile.objects.filter(username__in=["miha", "janez"]).update(is_superuser=True, is_staff=True)

        # I still shouldn't be able to do superuser stuff
        response = self.api_client.put("/account/impersonate", {"username": "janez"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Clearing cache, now Miha can do better stuff
        staff = UserProfile.objects.filter(is_staff=True)
        for user in staff:
            cache.delete(USER_CACHE_KEY.format(id=user.id))

        response = self.api_client.put("/account/impersonate", {"username": "janez"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
