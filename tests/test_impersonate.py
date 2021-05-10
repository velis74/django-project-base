from example.demo_django_base.models import UserProfile

from django.test import TestCase
from rest_framework.test import APIClient
from django.core.cache import cache


class TestImpersonateUserViewset(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_start(self):
        self.assertTrue(self.api_client.login(username='janez', password='janezjanez'), 'Not logged in')

        # Janez iz not superuser and is not allowd to impersonate
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
        response = self.api_client.post('/account/impersonate/start', {'email':'user1@user1.si'}, format='json')
        self.assertEqual(response.status_code, 200)

