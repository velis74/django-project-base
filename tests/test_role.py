import swapper
from django.contrib.auth.models import Group
from django.db.models import Model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from django_project_base.rest.project_role import ProjectRole
from django_project_base.rest_config import REST_API_CONFIG
from django_project_base.settings import TEST_USER_ONE_DATA
from example.demo_django_base.models import UserProfile
from tests.test_base import TestBase


class TestRole(TestBase):
    url: str = '/%s' % REST_API_CONFIG.ProjectRole.url
    project: Model

    def setUp(self):
        super().setUp()
        self.api_client = APIClient()
        self.project: Model = swapper.load_model('django_project_base', 'Project').objects.create(
            name='test-project', owner=UserProfile.objects.get(username=TEST_USER_ONE_DATA['username']),
            slug='test-project-slug',
        )
        response = self.api_client.post('/account/login/', {'login': TEST_USER_ONE_DATA['username'],
                                                            'password': TEST_USER_ONE_DATA['password'],
                                                            'return-type': 'json'}, format='json')
        self.api_client.credentials(HTTP_AUTHORIZATION='sessionid ' + response.data.get('sessionid', None))

    def __create_role(self, payload: dict = {}) -> Response:
        return self.api_client.post(self.url, {
            **{'name': 'test-role', 'project': self.project.pk}, **payload
        })

    def test_create_project_role(self):
        response: Response = self.__create_role()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        project_role: dict = response.json()
        self.assertEqual(project_role.get('name'), 'test-role')
        group: Group = Group.objects.get(pk=project_role.get(Group._meta.pk.name))
        self.assertEqual(group.name, f'{self.project.pk}{ProjectRole.delimiter}{project_role.get("name")}')

    def test_list_project_role(self):
        self.__create_role()
        list_response: Response = self.api_client.get(f'{self.url}?project={self.project.pk}')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.json()), 1)

    def test_retrieve_project_role(self):
        role_pk: int = self.__create_role().json().get(Group._meta.pk.name)
        retrieve_response: Response = self.api_client.get(f'{self.url}/{role_pk}')
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.json().get(Group._meta.pk.name), role_pk)

    def test_update_project_role(self):
        role_pk: int = self.__create_role().json().get(Group._meta.pk.name)
        update_response: Response = self.api_client.put(f'{self.url}/{role_pk}', {
            'name': 'new-role-name'
        })
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.json().get('name'), 'new-role-name')

    def test_delete_project_role(self):
        role_pk: int = self.__create_role().json().get(Group._meta.pk.name)
        delete_response: Response = self.api_client.delete(f'{self.url}/{role_pk}')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
