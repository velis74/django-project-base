from typing import List, Type

from django_project_base.notifications.base.channels.channel import Channel


class ProviderIntegration:
    channel: Type[Channel]
    settings: object

    def __init__(self, channel: Type[Channel], settings: object) -> None:
        super().__init__()
        self.channel = channel
        self.settings = settings

    def sender(self, project_slug: str) -> str:
        return self.settings.NOTIFICATION_SENDERS[project_slug]["settings"][self.channel.name]

    def clean_recipients(self, recipients: List[str]) -> List[str]:
        return [r for r in recipients if r not in ("", "None", None)]
