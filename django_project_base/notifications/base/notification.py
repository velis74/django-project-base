import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Type

from django.conf import settings

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.base.queable_notification_mixin import QueableNotificationMixin
from django_project_base.notifications.models import DjangoProjectBaseNotification, DjangoProjectBaseMessage
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

    def __init__(self, message: DjangoProjectBaseMessage, persist: bool = False,
                 level: Optional[NotificationLevel] = None,
                 locale: Optional[str] = None, delay: Optional[datetime] = None,
                 type: Optional[NotificationType] = None, recipients: List[settings.AUTH_USER_MODEL] = [],
                 **kwargs) -> None:
        super().__init__()
        assert isinstance(persist, bool), "Persist must be valid boolena value"
        self._persist = persist
        if level is not None:
            assert isinstance(level, str) and level in [
                l.value for l in NotificationLevel], "Invalid notification level value"
            self.level = level
        self.locale = locale
        if delay is not None:
            assert isinstance(delay, datetime) and delay > utc_now(), "Invalid delay value"
            self._delay = delay
        if type is not None:
            assert isinstance(type, str) and type in [
                t.value for t in NotificationType], "Invalid notification type value"
            self.type = type
        assert isinstance(recipients, list), "Recipients must be a list"
        self._recipients = recipients
        self._extra_data = kwargs
        assert isinstance(message, DjangoProjectBaseMessage), "Invalid value for message"
        self.message = message

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
            map(lambda f: str(f), filter(lambda d: d is not None, map(lambda c: c.id, self.via_channels))))
        notification: Optional[DjangoProjectBaseNotification] = None

        if self.persist:
            notification = DjangoProjectBaseNotification.objects.create(
                locale=self.locale,
                level=self.level or NotificationLevel.INFO.value,
                delayed_to=self.delay,
                required_channels=",".join(required_channels) if required_channels else None,
                type=self.type,
                message=self.message
            )

        if self.delay:
            if not self.persist:
                raise Exception('Delayed notification must be persisted')
            notification.save()
            notification.recipients.add(*self._recipients)
            self.enqueue_notification(notification)
            return notification

        sent_channels: list = []
        failed_channels: list = []

        for channel in self.via_channels:
            try:
                channel.send(self, **self._extra_data)
                sent_channels.append(channel)
            except Exception as e:
                logging.getLogger(__name__).error(e)
                failed_channels.append(channel)

        if self.persist:
            notification.sent_channels = ",".join(list(
                map(lambda f: str(f),
                    filter(lambda d: d is not None, map(lambda c: c.id, sent_channels))))) if sent_channels else None
            notification.failed_channels = ",".join(list(
                map(lambda f: str(f), filter(lambda d: d is not None,
                                             map(lambda c: c.id, failed_channels))))) if failed_channels else None
            notification.sent_at = utc_now()
            notification.save()
            notification.recipients.add(*self._recipients)
        return notification
