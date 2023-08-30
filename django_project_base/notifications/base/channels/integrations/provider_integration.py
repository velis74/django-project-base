from typing import List, Type

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.models import DjangoProjectBaseNotification


class ProviderIntegration:
    channel: Type[Channel]
    settings: object

    def __init__(self, channel: Type[Channel], settings: object) -> None:
        super().__init__()
        self.channel = channel
        self.settings = settings

    def sender(self, notification: DjangoProjectBaseNotification) -> str:
        _sender = getattr(notification, "sender", {}).get(self.channel.name)
        assert _sender, "Notification sender is required"
        return _sender

    def clean_recipients(self, recipients: List[str]) -> List[str]:
        return [r for r in recipients if r not in ("", "None", None)]
