from django.core.cache import cache
from rest_framework.test import APIClient

from django_project_base.base.auth_backends import UsersCachingBackend
from django_project_base.settings import USER_CACHE_KEY
from example.demo_django_base.models import UserProfile
from tests.test_base import TestBase


class TestUsersCachingBackend(TestBase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_caching_for_bulk_update(self):
        self.assertTrue(self.api_client.login(username="miha", password="mihamiha"), "Not logged in")
        miha = UserProfile.objects.get(username="miha")

        self.assertFalse(UsersCachingBackend().get_user(miha.id).is_superuser)
        self.assertIsNotNone(cache.get(USER_CACHE_KEY.format(id=miha.id)))

        UserProfile.objects.filter(username__in=["miha", "janez"]).update(is_superuser=True, is_staff=True)

        # Still cached, so the flip above isn't visible yet
        self.assertFalse(UsersCachingBackend().get_user(miha.id).is_superuser)

        # Clearing cache picks up the change
        staff = UserProfile.objects.filter(is_staff=True)
        for user in staff:
            cache.delete(USER_CACHE_KEY.format(id=user.id))

        self.assertTrue(UsersCachingBackend().get_user(miha.id).is_superuser)
