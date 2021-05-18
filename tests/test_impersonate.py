from django.core.cache import cache
from django.test import TestCase
from example.demo_django_base.models import UserProfile
from rest_framework.test import APIClient


class TestImpersonateUserViewset(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_impersonate(self):
        self.assertTrue(self.api_client.login(username='janez', password='janezjanez'), 'Not logged in')

        # Janez is not superuser and is not allowed to impersonate
        response = self.api_client.post('/account/impersonate/start', {'email': 'user1@user1.si'}, format='json')
        self.assertEqual(response.status_code, 403)

        # make Janez a superuser
        janez = UserProfile.objects.get(username='janez')
        janez.is_staff = True
        janez.is_superuser = True
        janez.save()
        # delete user cache
        cache.delete('django-user-%d' % janez.id)

        # Now Janez should be able to impersonate
        response = self.api_client.post('/account/impersonate/start', {'email': 'user1@user1.si'}, format='json')
        self.assertEqual(response.status_code, 200)

        # Check if is impersonated
        response = self.api_client.get('/account/profile/1', {}, format='json')
        self.assertEqual(response.status_code, 200)
        # TODO check for is_impersonated value

        response = self.api_client.post('/account/impersonate/end', {}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_impersonate_with_username(self):
        self.assertTrue(self.api_client.login(username='janez', password='janezjanez'), 'Not logged in')

        # make Janez a superuser
        janez = UserProfile.objects.get(username='janez')
        janez.is_staff = True
        janez.is_superuser = True
        janez.save()
        # delete user cache
        cache.delete('django-user-%d' % janez.id)

        response = self.api_client.post('/account/impersonate/start', {'username': 'miha'}, format='json')
        self.assertEqual(response.status_code, 200)
        response = self.api_client.post('/account/impersonate/end', {}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_impersonate_with_id(self):
        self.assertTrue(self.api_client.login(username='janez', password='janezjanez'), 'Not logged in')

        # make Janez a superuser
        janez = UserProfile.objects.get(username='janez')
        janez.is_staff = True
        janez.is_superuser = True
        janez.save()
        # delete user cache
        cache.delete('django-user-%d' % janez.id)

        response = self.api_client.post('/account/impersonate/start', {'id': 1}, format='json')
        self.assertEqual(response.status_code, 200)
        response = self.api_client.post('/account/impersonate/end', {}, format='json')
        self.assertEqual(response.status_code, 200)
