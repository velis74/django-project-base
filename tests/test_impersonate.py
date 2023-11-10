from rest_framework import status
from rest_framework.test import APIClient

from django_project_base.base.auth_backends import user_cache_invalidate
from example.demo_django_base.models import UserProfile
from tests.test_base import TestBase


class TestImpersonateUserViewset(TestBase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_impersonate(self):
        self.assertTrue(self._login_with_test_user_two(), "Not logged in")

        # Janez is not superuser and is not allowed to impersonate
        response = self.api_client.put("/account/impersonate", {"email": "user1@user1.si"}, format="json")
        self.assertEqual(response.status_code, 403)

        # make Janez a superuser
        janez = UserProfile.objects.get(username="janez")
        janez.is_staff = True
        janez.is_superuser = True
        janez.save()
        # delete user cache
        user_cache_invalidate(janez)

        # Now Janez should be able to impersonate
        response = self.api_client.put("/account/impersonate", {"email": "user1@user1.si"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.api_client.delete("/account/impersonate", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_impersonate_with_username(self):
        self.assertTrue(self._login_with_test_user_two(), "Not logged in")

        # make Janez a superuser
        janez = UserProfile.objects.get(username="janez")
        janez.is_staff = True
        janez.is_superuser = True
        janez.save()
        # delete user cache
        user_cache_invalidate(janez)

        response = self.api_client.put("/account/impersonate", {"username": "miha"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.api_client.delete("/account/impersonate", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_impersonate_with_id(self):
        self.assertTrue(self._login_with_test_user_two(), "Not logged in")

        # make Janez a superuser
        janez = UserProfile.objects.get(username="janez")
        janez.is_staff = True
        janez.is_superuser = True
        janez.save()
        # delete user cache
        user_cache_invalidate(janez)

        response = self.api_client.put("/account/impersonate", {"id": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.api_client.delete("/account/impersonate", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
