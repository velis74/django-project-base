import swapper
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient

from django_project_base.settings import TEST_USER_ONE_DATA
from example.demo_django_base.models import UserProfile
from tests.test_base import TestBase


class TestProjectSettings(TestBase):
    url: str = "/project-settings"

    def setUp(self):
        super().setUp()
        self.settingsModel = swapper.load_model("django_project_base", "ProjectSettings")
        self.api_client = APIClient()
        self._login_with_test_user_one()
        self.project = swapper.load_model("django_project_base", "Project").objects.create(
            **{
                "name": "test-project",
                "owner": UserProfile.objects.get(username=TEST_USER_ONE_DATA["username"]),
                "slug": get_random_string(length=8),
            }
        )
        self._create_fixtures()

    def _create_fixtures(self):
        self.settingsModel.objects.create(
            **{
                "name": "test",
                "description": "test",
                "value": "test",
                "value_type": self.settingsModel.VALUE_TYPE_CHAR,
                "project": self.project,
            }
        )

    def test_list_settings(self):
        self.assertEqual(1, len(self.api_client.get(self.url, HTTP_CURRENT_PROJECT=self.project.slug).data))
