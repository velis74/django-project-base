from enum import Enum


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
    def channel(identifier: int):
        if identifier == ChannelIdentifier.MAIL.value:
            from django_project_base.notifications.base.channels.mail_channel import MailChannel

            return MailChannel()
        raise NotImplementedError
