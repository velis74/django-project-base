import os
from pathlib import Path

from django.conf import settings
from django.utils.crypto import get_random_string

from django_project_base.settings_parser import parse_settings

DJANGO_PROJECT_BASE_SETTINGS = (
    {
        "name": "DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES",
        "default": {
            "project": {"value_name": "current_project_slug", "url_part": "project-"},
            "language": {"value_name": "current_language", "url_part": "language-"},
        },
    },
    {
        "name": "DJANGO_PROJECT_BASE_SLUG_FIELD_NAME",
        "default": "slug",
    },
    {
        "name": "REST_REGISTRATION",
        "default": {
            "RESET_PASSWORD_VERIFICATION_EMAIL_SENDER": "django_project_base.account.service.reset_password_email_service.send_reset_password_verification_email",  # noqa: E501
            "RESET_PASSWORD_VERIFICATION_URL": "/#reset-user-password/",
            "VERIFICATION_FROM_EMAIL": "",
            "SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL": True,
            "RESET_PASSWORD_VERIFICATION_ENABLED": True,
            "RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM": True,
            "SEND_RESET_PASSWORD_LINK_USER_FINDER": "django_project_base.account.service.reset_password_email_service.find_user_by_send_reset_password_link_data",  # noqa: E501
        },
    },
    {"name": "EMAIL_HOST_USER", "default": ""},
    {
        "name": "EMAIL_PROVIDER",
        "default": "django_project_base.notifications.base.channels.integrations.aws_ses.AwsSes",
    },
    # this settings silences (rest_registration.E013) SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL
    # is set but email field is not unique
    # todo: TASK https://taiga.velis.si/project/velis-django-project-admin/us/637?no-milestone=1
    {"name": "SILENCED_SYSTEM_CHECKS", "default": ["rest_registration.E013"]},
    {"name": "CONFIRMATION_CODE_TIMEOUT", "default": 600},
    {"name": "VERIFICATION_FROM_EMAIL", "default": ""},
    {"name": "EMAIL_BLOCKED_SMS_NOTIFICATION_RECIPIENT", "default": ""},
    {"name": "MAIL_TIMEOUT_AFTER_WSGI_RESTART", "default": 180},
    {"name": "NOTIFICATION_AGGREGATION_TIMEDELTA_SECONDS", "default": 240},
    {"name": "NOTIFICATION_LENGTH_SIMILARITY_BUFFER_VALUE", "default": 3},
)

USER_CACHE_KEY = "django-user-{id}"
CACHE_IMPERSONATE_USER = "impersonate-user-%d"

PROFILER_LOG_LONG_REQUESTS_COUNT = 50

PROFILE_REVERSE_FULL_NAME_ORDER = False

DELETE_PROFILE_TIMEDELTA = 3

DOCUMENTATION_DIRECTORY: str = str(Path().resolve()) + "/docs/build/"

TEST_USER_ONE_DATA = dict(
    username="miha", last_name="Novak", first_name="Miha", email="user1@user1.si", password="mihamiha"
)
TEST_USER_TWO_DATA = dict(
    username="janez", last_name="Novak", first_name="Janez", email="user2@user2.si", password="janezjanez"
)


def set_django_project_base_settings():
    parse_settings(DJANGO_PROJECT_BASE_SETTINGS)
