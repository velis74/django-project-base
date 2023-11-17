from rest_framework.test import APIClient

from tests.test_base import TestBase


class TestProfileViewSet(TestBase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_register_password_is_to_simillar_and_short(self):
        user = {
            "password": "string",
            "password_confirm": "string",
            "username": "string",
            "first_name": "string",
            "last_name": "string",
            "email": "user@example.com",
        }
        response = self.api_client.post("/account/register/", user, format="json")
        expected_response = (
            b'{"password":["The password is too similar to the username.","This password is too '
            b'short. It must contain at least 8 characters."],"non_field_errors":[]}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, expected_response)

    def test_register_password_is_to_short(self):
        user = {
            "password": "ad124sD",
            "password_confirm": "ad124sD",
            "username": "string",
            "first_name": "string",
            "last_name": "string",
            "email": "user@example.com",
        }
        response = self.api_client.post("/account/register/", user, format="json")
        expected_response = (
            b'{"password":["This password is too short. It must contain at least 8 characters."],'
            b'"non_field_errors":[]}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, expected_response)

    def test_register_password_is_to_similar(self):
        user = {
            "password": "string12",
            "password_confirm": "string12",
            "username": "string",
            "first_name": "string",
            "last_name": "string",
            "email": "user@example.com",
        }
        response = self.api_client.post("/account/register/", user, format="json")
        expected_response = b'{"password":["The password is too similar to the username."],"non_field_errors":[]}'
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, expected_response)

    def test_register_success(self):
        user = {
            "password": "asd124sD",
            "password_confirm": "asd124sD",
            "username": "string",
            "first_name": "string",
            "last_name": "string",
            "email": "user@example.com",
        }
        response = self.api_client.post("/account/register/", user, format="json")
        expected_response = (
            b'{"id":3,"username":"string","first_name":"string","last_name":"string",' b'"email":"user@example.com"}'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content, expected_response)

    def test_register_success_duplicate(self):
        user = {
            "password": "asd124sD",
            "password_confirm": "asd124sD",
            "username": "string",
            "first_name": "string",
            "last_name": "string",
            "email": "user@example.com",
        }
        response = self.api_client.post("/account/register/", user, format="json")
        expected_response = (
            b'{"id":3,"username":"string","first_name":"string","last_name":"string",' b'"email":"user@example.com"}'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content, expected_response)

        response = self.api_client.post("/account/register/", user, format="json")
        expected_response = b'{"username":["A user with that username already exists."]}'
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, expected_response)
