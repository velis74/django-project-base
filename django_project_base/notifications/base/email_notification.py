from datetime import datetime
from typing import List, Optional, Type

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.channels.mail_channel import MailChannel
from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.base.notification import Notification
from django_project_base.notifications.models import DjangoProjectBaseMessage


class EMailNotification(Notification):
    def __init__(
        self, delay: Optional[datetime], message: DjangoProjectBaseMessage, locale: Optional[str] = None
    ) -> None:
        super().__init__(
            message=message,
            persist=True,
            level=NotificationLevel.INFO.value,
            locale=locale,
            delay=delay,
            type=NotificationType.STANDARD.value,
        )

    @property
    def via_channels(self) -> List[Type[Channel]]:
        return [MailChannel]
