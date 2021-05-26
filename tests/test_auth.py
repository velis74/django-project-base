import os

from django.test import TestCase
from rest_framework.test import APIClient


class TestLoginViewset(TestCase):
    url_prefix = '/'

    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_login_no_post_data(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login'),
                                        {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content,
                         b'{"login":["This field is required."],"password":["This field is required."]}')

    def test_login_no_post_login(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login'),
                                        {'password': 'mihamiha'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"login":["This field is required."]}')

    def test_login_no_post_password(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login'),
                                        {'login': 'miha'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"password":["This field is required."]}')

    def test_login_wrong_user(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login'),
                                        {'login': 'mihamiha', 'password': 'mihamiha'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"detail":"Login or password invalid."}')

    def test_login_wrong_password(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login'),
                                        {'login': 'miha', 'password': 'miha'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"detail":"Login or password invalid."}')

    def test_login(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login'),
                                        {'login': 'miha', 'password': 'mihamiha'}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_logout_not_authorized(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'logout'),
                                        {}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_logout(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login'),
                                        {'login': 'miha', 'password': 'mihamiha'}, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.api_client.post(os.path.join(self.url_prefix, 'logout'),
                                        {}, format='json')
        self.assertEqual(response.status_code, 200)


class TestChangePasswordViewset(TestCase):
    url_prefix = '/account'

    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_change_password(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login'),
                                        {'login': 'miha', 'password': 'mihamiha'}, format='json')
        self.assertEqual(response.status_code, 200)

        # Test to short password
        response = self.api_client.post(os.path.join(self.url_prefix, 'change_password'),
                                        {'old_password': 'mihamiha', 'password': 'janez', 'password_confirm': 'janez'},
                                        format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content,
                         b'{"password":["This password is too short. It must contain at least 8 characters."]}')

        # Test ok password
        response = self.api_client.post(os.path.join(self.url_prefix, 'change_password'),
                                        {'old_password': 'mihamiha', 'password': 'janezjanez',
                                         'password_confirm': 'janezjanez'},
                                        format='json')
        self.assertEqual(response.status_code, 200)

        response = self.api_client.post(os.path.join(self.url_prefix, 'login'),
                                        {'login': 'miha', 'password': 'janezjanez'}, format='json')
        self.assertEqual(response.status_code, 200)
