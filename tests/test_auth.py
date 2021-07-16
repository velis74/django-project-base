import os

from django.core.cache import cache
from django.test import TestCase
from example.demo_django_base.models import UserProfile
from rest_framework.test import APIClient


class TestLoginViewset(TestCase):
    url_prefix = '/account/'

    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_login_no_post_data(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login/'),
                                        {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content,
                         b'{"login":["This field is required."],"password":["This field is required."]}')

    def test_login_no_post_login(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login/'),
                                        {'password': 'mihamiha'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"login":["This field is required."]}')

    def test_login_no_post_password(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login/'),
                                        {'login': 'miha'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"password":["This field is required."]}')

    def test_login_wrong_user(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login/'),
                                        {'login': 'mihamiha', 'password': 'mihamiha'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"detail":"Login or password invalid."}')

    def test_login_wrong_password(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login/'),
                                        {'login': 'miha', 'password': 'miha'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'{"detail":"Login or password invalid."}')

    def test_login(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login/'),
                                        {'login': 'miha', 'password': 'mihamiha'}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_login_json(self):
        # make Miha a superuser
        miha = UserProfile.objects.get(username='miha')
        miha.is_staff = True
        miha.is_superuser = True
        miha.save()
        cache.delete('django-user-%d' % miha.id)

        response = self.api_client.post(os.path.join(self.url_prefix, 'login/'),
                                        {'login': 'miha', 'password': 'mihamiha', 'return-type': 'json'}, format='json')
        self.assertEqual(response.status_code, 200)

        self.api_client.credentials(HTTP_AUTHORIZATION='sessionid ' + response.data.get('sessionid', None))
        response = self.api_client.get(os.path.join(self.url_prefix, '/account/profile/current'),
                                       {'return-type': 'json'}, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.api_client.post('/account/impersonate/start', {'username': 'janez', 'return-type': 'json'},
                                        format='json')
        self.assertEqual(response.status_code, 200)

    def test_profile_destroy_my_profile_json(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login/'),
                                        {'login': 'miha', 'password': 'mihamiha', 'return-type': 'json'}, format='json')
        self.api_client.credentials(HTTP_AUTHORIZATION='sessionid ' + response.data.get('sessionid', None))
        response = self.api_client.get('/account/profile/current', {'return-type': 'json'}, format='json')
        self.assertEqual(response.status_code, 200)
        response = self.api_client.delete('/account/profile/current', {'return-type': 'json'}, format='json')
        self.assertEqual(response.status_code, 204)
        response = self.api_client.get('/account/profile/current', {'return-type': 'json'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_logout_not_authorized(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'logout/'),
                                        {}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_logout(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login/'),
                                        {'login': 'miha', 'password': 'mihamiha'}, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.api_client.post(os.path.join(self.url_prefix, 'logout/'),
                                        {}, format='json')
        self.assertEqual(response.status_code, 200)


class TestChangePasswordViewset(TestCase):
    url_prefix = '/account/'

    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_change_password(self):
        response = self.api_client.post(os.path.join(self.url_prefix, 'login/'),
                                        {'login': 'miha', 'password': 'mihamiha'}, format='json')
        self.assertEqual(response.status_code, 200)

        # Test to short password
        response = self.api_client.post('/account/change-password/',
                                        {'old_password': 'mihamiha', 'password': 'janez', 'password_confirm': 'janez'},
                                        format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content,
                         b'{"password":["This password is too short. It must contain at least 8 characters."]}')

        # Test ok password
        response = self.api_client.post(os.path.join(self.url_prefix, 'change-password/'),
                                        {'old_password': 'mihamiha', 'password': 'janezjanez',
                                         'password_confirm': 'janezjanez'},
                                        format='json')
        self.assertEqual(response.status_code, 200)

        response = self.api_client.post(os.path.join(self.url_prefix, 'login/'),
                                        {'login': 'miha', 'password': 'janezjanez'}, format='json')
        self.assertEqual(response.status_code, 200)


class TestSendResetPasswordLink(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_send_reset_password_link(self):
        response = self.api_client.post(os.path.join('/account/login/'),
                                        {'login': 'miha', 'password': 'mihamiha'}, format='json')
        self.assertEqual(response.status_code, 200)

        # Send password link is disabled, returns 404
        response = self.api_client.post('/account/send-reset-password-link/', {'login': 'miha'},
                                        format='json')
        self.assertEqual(response.status_code, 404)
