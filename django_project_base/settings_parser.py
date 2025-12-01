from collections.abc import Iterable
from typing import Any


def parse_settings(input_settings: tuple) -> None:
    from django.conf import settings

    for _setting in input_settings:
        setting_name: str = _setting["name"]
        setting_default_value: Any = _setting["default"]
        if hasattr(settings, setting_name):
            _setting_existing_val: Any = getattr(settings, setting_name)
            if isinstance(_setting_existing_val, (tuple, list)):
                _setting_existing_val: list = list(_setting_existing_val)
                if isinstance(setting_default_value, Iterable):
                    for v in setting_default_value:
                        _setting_existing_val.append(v)
                else:
                    _setting_existing_val.append(setting_default_value)
                _setting_existing_val: tuple = tuple(dict.fromkeys(_setting_existing_val))
                setattr(settings, setting_name, _setting_existing_val)
            elif isinstance(_setting_existing_val, dict):
                _setting = setting_default_value
                _setting.update(_setting_existing_val)
                setattr(settings, setting_name, _setting)
            else:
                pass
        else:
            setattr(settings, setting_name, setting_default_value)
