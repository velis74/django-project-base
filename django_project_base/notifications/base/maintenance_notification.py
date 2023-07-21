import uuid
from datetime import datetime
from typing import List, Optional, Type

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.base.notification import Notification
from django_project_base.notifications.models import DjangoProjectBaseMessage


class MaintenanceNotification(Notification):
    def __init__(self, delay: datetime, message: DjangoProjectBaseMessage, locale: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            persist=True,
            level=NotificationLevel.WARNING.value,
            locale=locale,
            delay=delay,
            type=NotificationType.MAINTENANCE.value,
            content_entity_context=str(uuid.uuid4()),
        )

    @property
    def via_channels(self) -> List[Type[Channel]]:
        return []
