import datetime
import json
import uuid
from typing import List, Optional, Type

import swapper
from django.conf import settings
from django.contrib.auth import get_user_model

from django_project_base.constants import EMAIL_SENDER_ID_SETTING_NAME, SMS_SENDER_ID_SETTING_NAME
from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.duplicate_notification_mixin import DuplicateNotificationMixin
from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.base.queable_notification_mixin import QueableNotificationMixin
from django_project_base.notifications.base.send_notification_mixin import SendNotificationMixin
from django_project_base.notifications.models import DjangoProjectBaseMessage, DjangoProjectBaseNotification


class Notification(QueableNotificationMixin, DuplicateNotificationMixin, SendNotificationMixin):
    _persist = False
    _delay = None
    _recipients = []
    _extra_data = {}
    type = NotificationType.STANDARD.value
    level = None
    locale = None
    message: DjangoProjectBaseMessage
    content_entity_context = ""
    _raw_recipents: str
    _project: Optional[object]

    _via_channels = List[Type[Channel]]
    _user = None

    def __init__(
        self,
        message: DjangoProjectBaseMessage,
        raw_recipents: List[str],
        project,
        persist: bool = False,
        level: Optional[NotificationLevel] = None,
        locale: Optional[str] = None,
        delay: Optional[int] = None,
        type: Optional[NotificationType] = None,
        recipients=None,
        content_entity_context="",
        channels=[],
        user=None,
        **kwargs,
    ) -> None:
        super().__init__()
        if recipients is None:
            recipients = []
        if type is None:
            type = NotificationType.STANDARD
        if level is None:
            level = NotificationLevel.INFO
        assert isinstance(persist, bool), "Persist must be valid boolean value"
        assert raw_recipents is not None, "Original recipients payload is required"
        self._raw_recipents = json.dumps(raw_recipents)
        self._persist = persist
        if level is not None:
            lvl = level.value if isinstance(level, NotificationLevel) else level
            assert lvl in [_level.value for _level in NotificationLevel], "Invalid notification level value"
            self.level = level if isinstance(level, NotificationLevel) else NotificationLevel(lvl)
        self.locale = locale
        if delay is not None:
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
        if channels:
            # TODO: check for supported channels
            self.via_channels = channels
        self._project = project
        self._user = user

    def __set_via_channels(self, val):
        self._via_channels = val

    def __get_via_channels(self):
        return self._via_channels

    via_channels = property(__get_via_channels, __set_via_channels)

    @property
    def delay(self) -> Optional[int]:
        return self._delay

    @property
    def persist(self) -> bool:
        return bool(self._persist)

    def send(self) -> DjangoProjectBaseNotification:
        required_channels: list = list(
            map(lambda f: str(f), filter(lambda d: d is not None, map(lambda c: c.name, self.via_channels)))
        )
        notification: DjangoProjectBaseNotification = DjangoProjectBaseNotification(
            locale=self.locale,
            level=self.level.value,
            delayed_to=self.delay,
            required_channels=",".join(required_channels) if required_channels else None,
            type=self.type.value,
            message=self.message,
            content_entity_context=str(self.content_entity_context)
            if self.content_entity_context
            else str(uuid.uuid4()),
            recipients=",".join(map(str, self._recipients)) if self._recipients else None,
            recipients_original_payload=self._raw_recipents,
            project_slug=self._project,
        )
        notification.user = self._user
        if self._project and (
            project := swapper.load_model("django_project_base", "Project").objects.filter(slug=self._project).first()
        ):
            from django_project_base.notifications.base.channels.mail_channel import MailChannel
            from django_project_base.notifications.base.channels.sms_channel import SmsChannel

            mail_settings = project.projectsettings_set.filter(
                name=EMAIL_SENDER_ID_SETTING_NAME, project=project
            ).first()
            sms_settings = project.projectsettings_set.filter(name=SMS_SENDER_ID_SETTING_NAME, project=project).first()
            notification.sender = {
                MailChannel.name: mail_settings.value if mail_settings else "",
                SmsChannel.name: sms_settings.value if sms_settings else "",
            }
        required_channels.sort()
        if self.persist:
            if self.handle_similar_notifications(notification=notification):
                return notification
            if not self.message.pk or not DjangoProjectBaseMessage.objects.filter(pk=self.message.pk).exists():
                self.message.save()
            notification.created_at = int(datetime.datetime.now().timestamp())
            notification.save()
        else:
            notification.created_at = None

        if self.delay:
            if not self.persist:
                raise Exception("Delayed notification must be persisted")
            from django.db import connection

            sttgs = connection.settings_dict

            sttgs["TIME_ZONE"] = None
            self._extra_data["DATABASE"] = {
                "PARAMS": connection.get_connection_params(),
                "SETTINGS": sttgs,
            }
            self._extra_data["SETTINGS"] = settings
            rec_list = []
            for usr in self._recipients:
                rec_list.append(
                    {
                        k: v
                        for k, v in get_user_model().objects.get(pk=usr).userprofile.__dict__.items()
                        if not k.startswith("_")
                    }
                )
            notification.recipients_list = rec_list
            self.enqueue_notification(notification, self._extra_data)
            return notification

        notification = self.make_send(notification, self._extra_data)

        return notification
