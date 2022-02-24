from django.db.models import Model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from django_project_base.rest.project import ProjectSerializer
from django_project_base.rest_config import REST_API_CONFIG
from django_project_base.settings import TEST_USER_ONE_DATA
from example.demo_django_base.models import UserProfile
from tests.test_base import TestBase


class TestProject(TestBase):
    url: str = '/%s' % REST_API_CONFIG.Project.url

    def setUp(self):
        super().setUp()
        self.api_client = APIClient()
        self._create_project()

    def _create_project(self, payload: dict = {}) -> Response:
        _payload: dict = {
            'name': 'test-project',
            'owner': UserProfile.objects.get(username=TEST_USER_ONE_DATA['username']).pk,
            'slug': 'slug-test-project',
        }
        _payload.update(payload)
        return self.api_client.post(self.url, _payload)

    def test_create_project(self):
        self.assertEqual(status.HTTP_201_CREATED, self._create_project().status_code)

    def test_list_project(self):
        list_response: Response = self.api_client.get(self.url)
        self.assertEqual(ProjectSerializer.Meta.model.objects.all().count(), len(list_response.data))

    def test_retrieve_project(self):
        retrieve_project_pk: Response = self.api_client.get(f'{self.url}/1')
        self.assertEqual(status.HTTP_200_OK, retrieve_project_pk.status_code)
        retrieve_project_slug: Response = self.api_client.get(f'{self.url}/{retrieve_project_pk.data["slug"]}')
        self.assertEqual(retrieve_project_pk.data[ProjectSerializer.Meta.model._meta.pk.name],
                         retrieve_project_slug.data[ProjectSerializer.Meta.model._meta.pk.name])

    def test_update_project(self):
        project: Model = ProjectSerializer.Meta.model.objects.last()
        update_project: Response = self.api_client.patch(f'{self.url}/{project.pk}', {'name': 'updated-name'})
        self.assertEqual(update_project.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(project.name, 'updated-name')
