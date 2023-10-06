from typing import List, Optional, Type

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.channels.mail_channel import MailChannel
from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.base.notification import Notification
from django_project_base.notifications.models import DjangoProjectBaseMessage


class EMailNotification(Notification):
    def __init__(
        self,
        message: DjangoProjectBaseMessage,
        raw_recipents,
        project,
        persist: bool = True,
        level: Optional[NotificationLevel] = None,
        locale: Optional[str] = None,
        delay: Optional[int] = None,
        type: Optional[NotificationType] = None,
        recipients=None,
        **kwargs,
    ) -> None:
        super().__init__(
            message=message,
            raw_recipents=raw_recipents,
            project=project,
            persist=persist,
            level=level,
            locale=locale,
            delay=delay,
            type=type,
            recipients=recipients,
            **kwargs,
        )

    @property
    def via_channels(self) -> List[Type[Channel]]:
        return [MailChannel]
