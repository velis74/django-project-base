from datetime import datetime
from typing import List, Type, Optional

from django.conf import settings

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.channels.mail_channel import MailChannel
from django_project_base.notifications.base.enums import NotificationLevel
from django_project_base.notifications.base.notification import Notification


class EmailNotification(Notification):

    def __init__(self, message, level: Optional[NotificationLevel] = None, locale: Optional[str] = None,
                 delay: Optional[datetime] = None, recipients: List[settings.AUTH_USER_MODEL] = [], **kwargs) -> None:
        super().__init__(message=message, persist=True, level=level, locale=locale, delay=delay, recipients=recipients, **kwargs)

        @property
        def via_channels(self) -> List[Type[Channel]]:
            return [MailChannel]
