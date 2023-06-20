from datetime import datetime
from typing import List, Optional, Type

from django.conf import settings

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.channels.mail_channel import MailChannel
from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.base.notification import Notification
from django_project_base.notifications.models import DjangoProjectBaseMessage


class EMailNotification(Notification):
    def __init__(
        self,
        message: DjangoProjectBaseMessage,
        persist: bool = False,
        level: Optional[NotificationLevel] = None,
        locale: Optional[str] = None,
        delay: Optional[datetime] = None,
        type: Optional[NotificationType] = None,
        recipients: List[settings.AUTH_USER_MODEL] = [],
        **kwargs
    ) -> None:
        super().__init__(message, persist, level, locale, delay, type, recipients, **kwargs)

    @property
    def via_channels(self) -> List[Type[Channel]]:
        return [MailChannel]
