import datetime
import uuid

from typing import List, Optional, Type

from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import PermissionDenied

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.channels.mail_channel import MailChannel
from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.base.notification import Notification
from django_project_base.notifications.models import DjangoProjectBaseMessage, DjangoProjectBaseNotification


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


class EMailNotificationWithListOfEmails(EMailNotification):
    def __init__(self, message: DjangoProjectBaseMessage, recipients, project, user, **kwargs) -> None:
        super().__init__(
            raw_recipents=recipients,
            message=message,
            project=project,
            recipients=recipients,
            persist=True,
            delay=int(datetime.datetime.now().timestamp()),
            user=user,
            **kwargs,
        )

    def send(self) -> DjangoProjectBaseNotification:
        from django_project_base.notifications.base.channels.mail_channel import MailChannel

        notification: DjangoProjectBaseNotification = DjangoProjectBaseNotification(
            delayed_to=self.delay,
            required_channels=f"{MailChannel.name}",
            message=self.message,
            content_entity_context=str(self.content_entity_context)
            if self.content_entity_context
            else str(uuid.uuid4()),
            recipients=",".join(map(str, self._recipients)) if self._recipients else None,
            recipients_original_payload=self._raw_recipents,
            project_slug=self._project,
        )

        notification = self._ensure_channels([MailChannel.name], notification, settings=settings)

        if self.handle_similar_notifications(notification=notification):
            return notification
        if not self.message.pk or not DjangoProjectBaseMessage.objects.filter(pk=self.message.pk).exists():
            self.message.save()
        notification.created_at = int(datetime.datetime.now().timestamp())
        notification.save()
        uuid_val = str(uuid.uuid4())
        notification.email_list = [
            dict(
                id=uuid_val,
                email=u,
                phone_number="",
            )
            for u in self._recipients
        ]
        self.enqueue_notification(notification, self._extra_data)
        return notification


class SystemEMailNotification(EMailNotification):
    system_mail_throttling_ck = "system-mail-throttling-ck"
    allowed_number_of_system_requests_per_minute = 5

    def __init__(
        self,
        message: DjangoProjectBaseMessage,
        recipients,
        **kwargs,
    ) -> None:
        super().__init__(
            message,
            raw_recipents=recipients,
            project=None,
            persist=True,
            level=None,
            locale=None,
            delay=int(datetime.datetime.now().timestamp()),
            type=None,
            recipients=recipients,
            is_system_notification=True,
            **kwargs,
        )

    def _get_system_email_cache_key(self) -> str:
        return f"{self.system_mail_throttling_ck}-{datetime.datetime.now().minute}"

    def _get_system_email_cache_value(self) -> List[float]:
        if ck_val := cache.get(self._get_system_email_cache_key()):
            return ck_val
        return []

    def _check_request_limit(self):
        if len(self._get_system_email_cache_value()) > self.allowed_number_of_system_requests_per_minute:
            raise PermissionDenied

    def _register_system_email(self):
        if ck_val := self._get_system_email_cache_value():
            if len(ck_val) > self.allowed_number_of_system_requests_per_minute + 1:
                return
            ck_val.append(datetime.datetime.now().timestamp())
            cache.set(self._get_system_email_cache_key(), ck_val, timeout=70)
            return
        cache.set(self._get_system_email_cache_key(), [datetime.datetime.now().timestamp()], timeout=70)

    def send(self) -> DjangoProjectBaseNotification:
        # throttling for system messages
        self._check_request_limit()
        self._register_system_email()
        return super().send()


class SystemEMailNotificationWithListOfEmails(EMailNotificationWithListOfEmails):
    def __init__(
        self,
        message: DjangoProjectBaseMessage,
        recipients,
        **kwargs,
    ) -> None:
        super().__init__(
            message,
            recipients,
            project=kwargs.pop("project", None),
            user=kwargs.pop("user", None),
            level=kwargs.pop("level", None),
            locale=kwargs.pop("locale", None),
            type=kwargs.pop("type", None),
            is_system_notification=True,
            **kwargs,
        )
