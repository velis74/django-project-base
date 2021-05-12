from django.test import TestCase
from example.demo_django_base.models import Project, UserProfile
from rest_framework.test import APIClient


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
