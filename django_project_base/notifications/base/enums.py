from enum import Enum
from typing import Optional, Union


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
    def channel(
        identifier: Union[int, str],
        extra_data: Optional[dict] = None,
        project_slug: Optional[str] = None,
        ensure_dlr_user=True,
    ) -> Optional["Channel"]:  # noqa: F821
        channel = next(
            iter(filter(lambda c: c.name == identifier or c.id == identifier, ChannelIdentifier.supported_channels())),
            None,
        )
        if channel:
            channel.provider = channel._find_provider(
                extra_settings=extra_data, setting_name=channel.provider_setting_name
            )
            channel.provider.ensure_credentials(extra_data=extra_data)
            channel.provider.ensure_dlr_user(project_slug) if ensure_dlr_user else False

            return channel
        return None
