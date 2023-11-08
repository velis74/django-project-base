import os

from rest_framework import status
from rest_framework.test import APIClient

from django_project_base.base.auth_backends import user_cache_invalidate
from example.demo_django_base.models import UserProfile
from tests.test_base import TestBase


class TestLoginViewset(TestBase):
    url_prefix = "/account/"

    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_login_no_post_data(self):
        response = self.api_client.post(os.path.join(self.url_prefix, "login"), {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content, b'{"login":["This field is required."],"password":["This field is required."]}'
        )

    def test_login_no_post_login(self):
        response = self.api_client.post(os.path.join(self.url_prefix, "login"), {"password": "mihamiha"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"login":["This field is required."]}')

    def test_login_no_post_password(self):
        response = self.api_client.post(os.path.join(self.url_prefix, "login"), {"login": "miha"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"password":["This field is required."]}')

    def test_login_wrong_user(self):
        response = self.api_client.post(
            os.path.join(self.url_prefix, "login"), {"login": "mihamiha", "password": "mihamiha"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"detail":"Login or password invalid."}')

    def test_login_wrong_password(self):
        response = self.api_client.post(
            os.path.join(self.url_prefix, "login"), {"login": "miha", "password": "miha"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"detail":"Login or password invalid."}')

    def test_login(self):
        response = self.api_client.post(
            os.path.join(self.url_prefix, "login"), {"login": "miha", "password": "mihamiha"}, format="json"
        )
        self.assertIsNotNone(response.cookies.get("sessionid", None))
        self.assertIsNotNone(response.cookies.get("csrftoken", None))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_json(self):
        # make Miha a superuser
        miha = UserProfile.objects.get(username="miha")
        miha.is_staff = True
        miha.is_superuser = True
        miha.save()
        user_cache_invalidate(miha)

        response = self.api_client.post(
            os.path.join(self.url_prefix, "login"),
            {"login": "miha", "password": "mihamiha", "return-type": "json"},
            format="json",
        )
        self.assertIsNone(response.cookies.get("sessionid", None))
        self.assertIsNone(response.cookies.get("csrftoken", None))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.api_client.credentials(HTTP_AUTHORIZATION="sessionid " + response.data.get("sessionid", None))
        response = self.api_client.get(
            os.path.join(self.url_prefix, "/account/profile/current"), {"return-type": "json"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.api_client.put("/account/impersonate", {"username": "janez"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_json_missing_session(self):
        response = self.api_client.post(
            os.path.join(self.url_prefix, "login"),
            {"login": "miha", "password": "mihamiha", "return-type": "json"},
            format="json",
        )
        self.assertIsNone(response.cookies.get("sessionid", None))
        self.assertIsNone(response.cookies.get("csrftoken", None))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.api_client.get(os.path.join(self.url_prefix, "/account/profile/current"), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.content, b'{"detail":"Authentication credentials were not provided."}')

    def test_profile_destroy_my_profile_json(self):
        response = self.api_client.post(
            os.path.join(self.url_prefix, "login"),
            {"login": "miha", "password": "mihamiha", "return-type": "json"},
            format="json",
        )
        self.api_client.credentials(HTTP_AUTHORIZATION="sessionid " + response.data.get("sessionid", None))
        response = self.api_client.get("/account/profile/current", {"return-type": "json"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.api_client.delete("/account/profile/current", {"return-type": "json"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.api_client.get("/account/profile/current", {"return-type": "json"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_not_authorized(self):
        response = self.api_client.post(os.path.join(self.url_prefix, "logout"), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout(self):
        response = self.api_client.post(
            os.path.join(self.url_prefix, "login"), {"login": "miha", "password": "mihamiha"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.api_client.post(os.path.join(self.url_prefix, "logout"), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestChangePasswordViewset(TestBase):
    url_prefix = "/account/"

    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_change_password(self):
        response = self.api_client.post(
            os.path.join(self.url_prefix, "login"), {"login": "miha", "password": "mihamiha"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test to short password
        response = self.api_client.post(
            os.path.join(self.url_prefix, "change-password/"),
            {"old_password": "mihamiha", "password": "janez", "password_confirm": "janez"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.content, b'{"password":["This password is too short. It must contain at least 8 characters."]}'
        )

        # Test ok password
        response = self.api_client.post(
            os.path.join(self.url_prefix, "change-password/"),
            {"old_password": "mihamiha", "password": "janezjanez", "password_confirm": "janezjanez"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.api_client.post(
            os.path.join(self.url_prefix, "login"), {"login": "miha", "password": "janezjanez"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestSendResetPasswordLink(TestBase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_send_reset_password_link(self):
        response = self.api_client.post(
            os.path.join("/account/login"), {"login": "miha", "password": "mihamiha"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.api_client.post("/account/send-reset-password-link/", {"email": "miha"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        from django_project_base.settings import TEST_USER_ONE_DATA

        response = self.api_client.post(
            "/account/send-reset-password-link/", {"email": TEST_USER_ONE_DATA}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
