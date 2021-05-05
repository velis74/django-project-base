from django.test import TestCase

from example.demo_django_base.models import Project


class TestProject(TestCase):
    def test_construction(self):
        assert Project()
