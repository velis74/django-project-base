from enum import Enum
from typing import Optional, Union

from django_project_base.notifications.base.channels.channel import Channel


class NotificationType(Enum):
    MAINTENANCE = "maintenance"
    STANDARD = "standard"


class NotificationLevel(Enum):
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ChannelIdentifier(Enum):
    MAIL = 0
    SMS = 1
    WEBSOCKET = 3

    @staticmethod
    def supported_channels() -> tuple:
        from django_project_base.notifications.base.channels.mail_channel import MailChannel
        from django_project_base.notifications.base.channels.sms_channel import SmsChannel

        return MailChannel(), SmsChannel()

    @staticmethod
    def channel(identifier: Union[int, str]) -> Optional[Channel]:
        return next(
            iter(filter(lambda c: c.name == identifier or c.id == identifier, ChannelIdentifier.supported_channels())),
            None,
        )
