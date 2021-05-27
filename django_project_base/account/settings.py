from django_project_base.account.social_auth.settings import SOCIAL_AUTH_SETTINGS

ACCOUNT_SETTINGS = []

for set in SOCIAL_AUTH_SETTINGS:
    ACCOUNT_SETTINGS.append(set)

ACCOUNT_SETTINGS = tuple(ACCOUNT_SETTINGS)
