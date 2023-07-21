from abc import ABC, abstractmethod


class Channel(ABC):
    id = None

    provider = None

    @staticmethod
    @abstractmethod
    def send(notification: "Notification", mail_content_entity_context: str = "", **kwargs) -> int:  # noqa: F821
        pass
