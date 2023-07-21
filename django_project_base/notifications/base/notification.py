import logging
import random
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Type

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.base.queable_notification_mixin import QueableNotificationMixin
from django_project_base.notifications.models import DjangoProjectBaseMessage, DjangoProjectBaseNotification
from django_project_base.notifications.utils import utc_now


class Notification(ABC, QueableNotificationMixin):
    _persist = False
    _delay = None
    _recipients = []
    _extra_data = {}
    type = NotificationType.STANDARD.value
    level = None
    locale = None
    message: DjangoProjectBaseMessage
    content_entity_context = ""

    def __init__(
        self,
        message: DjangoProjectBaseMessage,
        persist: bool = False,
        level: Optional[NotificationLevel] = None,
        locale: Optional[str] = None,
        delay: Optional[datetime] = None,
        type: Optional[NotificationType] = None,
        recipients: List[int] = [],
        content_entity_context="",
        **kwargs,
    ) -> None:
        super().__init__()
        assert isinstance(persist, bool), "Persist must be valid boolean value"
        self._persist = persist
        if level is not None:
            lvl = level.value if isinstance(level, NotificationLevel) else level
            assert lvl in [_level.value for _level in NotificationLevel], "Invalid notification level value"
            self.level = level if isinstance(level, NotificationLevel) else NotificationLevel(lvl)
        self.locale = locale
        if delay is not None:
            assert isinstance(delay, datetime) and delay > utc_now(), "Invalid delay value"
            self._delay = delay
        if type is not None:
            typ = type.value if isinstance(type, NotificationType) else type
            assert typ in [t.value for t in NotificationType], "Invalid notification type value"
            self.type = type if isinstance(type, NotificationType) else NotificationType(typ)
        assert isinstance(recipients, list), "Recipients must be a list"
        self._recipients = recipients
        self._extra_data = kwargs
        assert isinstance(message, DjangoProjectBaseMessage), "Invalid value for message"
        self.message = message
        self.content_entity_context = content_entity_context

    @property
    @abstractmethod
    def via_channels(self) -> List[Type[Channel]]:
        return []

    @property
    def delay(self) -> Optional[datetime]:
        return self._delay

    @property
    def persist(self) -> bool:
        return bool(self._persist)

    def send(self) -> DjangoProjectBaseNotification:
        required_channels: list = list(
            map(lambda f: str(f), filter(lambda d: d is not None, map(lambda c: c.id, self.via_channels)))
        )
        notification: Optional[DjangoProjectBaseNotification] = None

        if self.persist:
            if not self.message.pk or not DjangoProjectBaseMessage.objects.filter(pk=self.message.pk).exists():
                self.message.save()
            notification = DjangoProjectBaseNotification.objects.create(
                locale=self.locale,
                level=self.level.value,
                delayed_to=self.delay,
                required_channels=",".join(required_channels) if required_channels else None,
                type=self.type.value,
                message=self.message,
                content_entity_context=str(self.content_entity_context)
                if self.content_entity_context
                else str(uuid.uuid4()),
            )

        if self.delay:
            if not self.persist:
                raise Exception("Delayed notification must be persisted")
            notification.save()
            notification.recipients = (notification.recipients or []) + self._recipients
            self.enqueue_notification(notification)
            return notification

        sent_channels: list = []
        failed_channels: list = []
        exceptions = ""
        for channel in self.via_channels:
            try:
                channel.send(self, **self._extra_data)
                sent_channels.append(channel)
            except Exception as e:
                logging.getLogger(__name__).error(e)
                failed_channels.append(channel)
                exceptions += f"{str(e)}\n\n"

        if self.persist:
            notification.sent_channels = (
                ",".join(
                    list(map(lambda f: str(f), filter(lambda d: d is not None, map(lambda c: c.id, sent_channels))))
                )
                if sent_channels
                else None
            )
            notification.failed_channels = (
                ",".join(
                    list(map(lambda f: str(f), filter(lambda d: d is not None, map(lambda c: c.id, failed_channels))))
                )
                if failed_channels
                else None
            )
            notification.sent_at = utc_now()
            notification.exceptions = exceptions if exceptions else None
            notification.save(update_fields=["sent_at", "sent_channels", "failed_channels", "exceptions"])
            notification.recipients = (notification.recipients or []) + self._recipients
        return notification
