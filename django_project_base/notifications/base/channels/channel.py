from abc import ABC, abstractmethod
from typing import List, Optional, Union

from django.conf import settings
from django.utils.module_loading import import_string


class Channel(ABC):
    id = None

    name = ""

    notification_price = 0

    provider_setting_name = ""

    @staticmethod
    def provider(extra_settings: Optional[dict], setting_name: str) -> "ProviderIntegration":  # noqa F821
        def get_first_provider(val: Union[str, List]) -> "ProviderIntegration":  # noqa F821
            if val and isinstance(val, list):
                return import_string(val[0])()

            return import_string(val)()

        if extra_settings and getattr(extra_settings.get("SETTINGS", object()), setting_name, None):
            return get_first_provider(getattr(extra_settings["SETTINGS"], setting_name))
        return get_first_provider(getattr(settings, setting_name, ""))

    @staticmethod
    @abstractmethod
    def send(notification: "DjangoProjectBaseNotification", extra_data, **kwargs) -> int:  # noqa: F821
        pass
