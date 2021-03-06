from abc import ABC, abstractmethod


class Channel(ABC):
    id = None

    @staticmethod
    @abstractmethod
    def send(notification: "Notification", **kwargs) -> None:  # noqa: F821
        pass
