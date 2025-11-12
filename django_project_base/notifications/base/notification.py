import datetime
import json
import uuid

from typing import List, Optional, Type

import swapper

from django.conf import Settings, settings
from django.contrib.auth import get_user_model

from django_project_base.constants import (
    EMAIL_SENDER_ID_SETTING_NAME,
    SMS_SENDER_ID_SETTING_NAME,
    USE_EMAIL_IF_RECIPIENT_HAS_NO_PHONE_NUMBER,
)
from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.duplicate_notification_mixin import DuplicateNotificationMixin
from django_project_base.notifications.base.enums import ChannelIdentifier, NotificationLevel, NotificationType
from django_project_base.notifications.base.queable_notification_mixin import QueableNotificationMixin
from django_project_base.notifications.base.send_notification_service import SendNotificationService
from django_project_base.notifications.models import DjangoProjectBaseMessage, DjangoProjectBaseNotification
from django_project_base.utils import get_host_url


class Notification(QueableNotificationMixin, DuplicateNotificationMixin):
    _persist = False
    _delay = None
    _recipients = []
    _extra_data = {}
    type = NotificationType.STANDARD.value
    level = None
    locale = None
    message: DjangoProjectBaseMessage
    content_entity_context = ""
    send_notification_sms = False
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
        send_notification_sms=False,
        **kwargs,
    ) -> None:
        super().__init__()
        if recipients is None:
            recipients = []
        if type is None:
            type = NotificationType.STANDARD
        if level is None:
            level = NotificationLevel.INFO
        self.send_notification_sms = send_notification_sms
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
        self._extra_data = kwargs or {}
        assert isinstance(message, DjangoProjectBaseMessage), "Invalid value for message"
        self.message = message
        self.content_entity_context = content_entity_context
        if channels:
            # TODO: check for supported channels
            self.via_channels = channels
        self._project = project
        self._user = user

    @staticmethod
    def resend(notification: DjangoProjectBaseNotification, user_pk: Optional[str] = None):
        if user_pk == "None":
            user_pk = None
        notification.user = user_pk or (notification.extra_data or {}).get("user")
        from django_project_base.notifications.rest.notification import MessageToListField

        recipients: List[str] = MessageToListField.parse(json.loads(notification.recipients_original_payload))
        notification.recipients = ",".join(map(str, recipients)) if recipients else None
        notification.recipients_original_payload_search = None
        notification.sender = Notification._get_sender_config(notification.project_slug)
        mail_fallback: bool = (
            swapper.load_model("django_project_base", "ProjectSettings")
            .objects.get(name=USE_EMAIL_IF_RECIPIENT_HAS_NO_PHONE_NUMBER, project__slug=notification.project_slug)
            .python_value
            if notification.project_slug
            else False
        )
        notification.email_fallback = mail_fallback
        notification.save(update_fields=["recipients", "recipients_original_payload_search"])
        SendNotificationService(settings=settings, use_default_db_connection=True).make_send(
            notification, {}, resend=True
        )

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

    @staticmethod
    def _get_sender_config(project_slug: Optional[str]) -> dict:
        from django_project_base.notifications.base.channels.mail_channel import MailChannel
        from django_project_base.notifications.base.channels.sms_channel import SmsChannel

        if project_slug and (
            project := swapper.load_model("django_project_base", "Project").objects.filter(slug=project_slug).first()
        ):
            project_settings_model = swapper.load_model("django_project_base", "ProjectSettings")
            mail_settings = project_settings_model.objects.filter(
                name=EMAIL_SENDER_ID_SETTING_NAME, project=project
            ).first()
            sms_settings = project_settings_model.objects.filter(
                name=SMS_SENDER_ID_SETTING_NAME, project=project
            ).first()
            return {
                MailChannel.name: mail_settings.python_value if mail_settings else "",
                SmsChannel.name: sms_settings.python_value if sms_settings else "",
            }
        return {
            MailChannel.name: "",
            SmsChannel.name: "",
        }

    def send(self) -> DjangoProjectBaseNotification:
        required_channels: list = list(
            map(lambda f: str(f), filter(lambda d: d is not None, map(lambda c: c.name, self.via_channels)))
        )
        self._extra_data["user"] = self._user
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
            send_notification_sms=self.send_notification_sms,
            send_notification_sms_text=None,
            extra_data=self._extra_data,
        )

        notification = self._ensure_channels(channels=required_channels, notification=notification, settings=settings)

        required_channels.sort()
        if self.persist:
            if self.handle_similar_notifications(notification=notification):
                return notification
            if self.message._state.adding:
                self.message.save()
            notification.created_at = int(datetime.datetime.now().timestamp())
            notification.save()
        else:
            notification.created_at = None

        if self.delay:
            if not self.persist:
                raise Exception("Delayed notification must be persisted")

            rec_list = self._extra_data.get("a_recipients_list") or []
            if len(rec_list) == 0:
                for usr in self._recipients:
                    rec_list.append(
                        {
                            k: v
                            for k, v in get_user_model().objects.get(pk=usr).userprofile.__dict__.items()
                            if not k.startswith("_")
                        }
                    )
            notification.recipients_list = rec_list
            ext_data = self._extra_data.get("a_extra_data") or self._extra_data
            notification.extra_data = ext_data
            notification.save(update_fields=["extra_data"])
            self.enqueue_notification(notification, extra_data=ext_data)
            return notification

        if not self.delay:
            SendNotificationService(settings=settings, use_default_db_connection=True).make_send(
                notification, self._extra_data, resend=False
            )
        else:
            if not self.persist:
                raise Exception("Delayed notification must be persisted")
            mail_fallback: bool = (
                swapper.load_model("django_project_base", "ProjectSettings")
                .objects.get(name=USE_EMAIL_IF_RECIPIENT_HAS_NO_PHONE_NUMBER, project__slug=notification.project_slug)
                .python_value
                if notification.project_slug
                else False
            )
            rec_list = []
            for usr in self._recipients:
                rec_list.append(
                    {
                        k: v
                        for k, v in get_user_model().objects.get(pk=usr).userprofile.__dict__.items()
                        if not k.startswith("_") and isinstance(v, (str, list, tuple, int, float))
                    }
                )
            notification.extra_data["recipients-list"] = rec_list
            notification.extra_data["sender"] = notification.sender
            notification.extra_data["mail-fallback"] = mail_fallback
            notification.save(update_fields=["extra_data"])

        return notification

    def _ensure_channels(
        self,
        channels: List[str],
        notification: DjangoProjectBaseNotification,
        settings: Optional[Settings] = None,
    ) -> DjangoProjectBaseNotification:
        from django_project_base.notifications.base.channels.mail_channel import MailChannel

        extra_data = self._extra_data.get("a_extra_data") or self._extra_data
        settings = self._extra_data.get("a_settings") or settings
        for channel_name in channels:
            # ensure dlr user and check providers
            channel = ChannelIdentifier.channel(channel_name, settings=settings, project_slug=self._project)

            if not channel and extra_data.get("is_system_notification"):
                continue

            assert channel

            if self.send_notification_sms and channel.name == MailChannel.name:
                notification.send_notification_sms_text = channel.provider.get_send_notification_sms_text(
                    notification=notification,
                    host_url=extra_data.get("host_url", ""),  # noqa: E126
                )

        notification.user = self._user

        notification.sender = self._extra_data.get("a_sender") or Notification._get_sender_config(self._project)

        mail_fallback = False
        if not self._extra_data.get("a_sender"):
            mail_fallback: bool = (
                swapper.load_model("django_project_base", "ProjectSettings")
                .objects.get(name=USE_EMAIL_IF_RECIPIENT_HAS_NO_PHONE_NUMBER, project__slug=notification.project_slug)
                .python_value
                if notification.project_slug
                else False
            )
        notification.email_fallback = mail_fallback

        if self._extra_data.get("is_system_notification"):
            notification.sender[MailChannel.name] = getattr(settings, "SYSTEM_EMAIL_SENDER_ID", "")
            from django_project_base.notifications.base.channels.sms_channel import SmsChannel

            notification.sender[SmsChannel.name] = getattr(settings, "SYSTEM_SMS_SENDER_ID", "")

        return notification

    @staticmethod
    def create_notification(
        request,
        subject,
        body,
        recipients,
        send_on_channels,
        send_notification_sms,
        raw_recipients=None,
        project_slug=None,
        save_only=False,
        delayed_to=None,
    ):
        if not project_slug:
            project_slug = (
                swapper.load_model("django_project_base", "Project")
                .objects.get(slug=request.selected_project_slug)
                .slug
            )
        if not raw_recipients:
            raw_recipients = recipients

        host_url = get_host_url(request)
        delayed_to = (
            DjangoProjectBaseNotification.DELAYED_INDEFINITELY
            if save_only
            else delayed_to or int(datetime.datetime.now().timestamp())
        )
        if isinstance(delayed_to, datetime.datetime):
            delayed_to = int(delayed_to.timestamp())
        notification = Notification(
            message=DjangoProjectBaseMessage(
                subject=subject,
                body=body,
                footer="",
                content_type=DjangoProjectBaseMessage.HTML,
            ),
            raw_recipents=raw_recipients,
            project=project_slug,
            recipients=recipients,
            delay=delayed_to,
            channels=[
                ChannelIdentifier.channel(c, settings=settings, project_slug=None).__class__ for c in send_on_channels
            ],
            persist=True,
            user=request.user.pk,
            send_notification_sms=send_notification_sms,
            host_url=host_url,
        )
        notification.send()
        return notification
