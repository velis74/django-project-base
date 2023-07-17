from enum import Enum


class NotificationType(Enum):
    MAINTENANCE = 'maintenance'
    STANDARD = 'standard'


class NotificationLevel(Enum):
    SUCCESS = 'success'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'


class ChannelIdentifier(Enum):
    MAIL = 0
    SMS = 1
    WEBSOCKET = 3
