from django.test import TestCase
from rest_framework.test import APIClient

from example.demo_django_base.models import Project, UserProfile


class TestProject(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_construction(self):
        assert Project()


class TestProfile(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_construction(self):
        assert UserProfile()
