from abc import ABC, abstractmethod


class Channel(ABC):
    id = None

    provider = None

    name = ""

    @staticmethod
    @abstractmethod
    def send(notification: "DjangoProjectBaseNotification", extra_data, **kwargs) -> int:  # noqa: F821
        pass
