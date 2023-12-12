"""Get enabled social auth providers configuration."""
import importlib

from collections import namedtuple
from functools import reduce
from typing import Iterable, List

from django.conf import settings

from django_project_base.constants import ACCOUNT_URL_PREFIX

SocialProviderItem = namedtuple("SocialProviderItem", ("name", "title", "url"))


def get_social_providers() -> List[SocialProviderItem]:
    config: List[SocialProviderItem] = []

    authentication_backends: Iterable = filter(lambda b: "social_core" in b, settings.AUTHENTICATION_BACKENDS)
    existing_settings: list = list(
        map(lambda e: e.lower(), filter(lambda s: s.lower().startswith("social_auth_"), dir(settings)))
    )
    for auth_bckend in authentication_backends:
        # first, we import the auth backend
        auth_backend = importlib.import_module(".".join(auth_bckend.split(".")[:3]))
        # next we go into the backend's implementation module
        auth_module = reduce(lambda x, attr_name: getattr(x, attr_name), auth_bckend.split(".")[3:], auth_backend)
        # and finally get the backend's module name
        name: str = auth_module.name

        search_query: str = next(iter(name.split("-"))).lower()
        search_results: list = list(
            filter(lambda d: search_query in d and (d.endswith("_key") or d.endswith("_secret")), existing_settings)
        )
        if search_results:
            config.append(
                SocialProviderItem(name, search_query.title(), "/%s/social/login/%s/" % (ACCOUNT_URL_PREFIX, name))
            )

    return config
