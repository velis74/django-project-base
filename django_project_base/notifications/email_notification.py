import datetime
import uuid
from typing import List, Optional, Type

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

        notification = self._ensure_channels([MailChannel.name], notification)

        if self.handle_similar_notifications(notification=notification):
            return notification
        if not self.message.pk or not DjangoProjectBaseMessage.objects.filter(pk=self.message.pk).exists():
            self.message.save()
        notification.created_at = int(datetime.datetime.now().timestamp())
        notification.save()
        self._set_db()
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
