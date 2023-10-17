from django.test import TestCase

from django_project_base.settings import TEST_USER_ONE_DATA, TEST_USER_TWO_DATA


class TestBase(TestCase):
    def __login_with_user(self, user_data: dict) -> bool:
        return self.api_client.login(username=user_data["username"], password=user_data["password"])

    def _login_with_test_user_one(self) -> bool:
        return self.__login_with_user(TEST_USER_ONE_DATA)

    def _login_with_test_user_two(self) -> bool:
        return self.__login_with_user(TEST_USER_TWO_DATA)
