import logging

from django.conf import Settings
from django.utils import timezone

from django_project_base.constants import NOTIFICATION_QUEUE_NAME
from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.models import DjangoProjectBaseNotification


class SendNotificationService(object):
    settings: Settings
    use_default_db_connection = False

    def __init__(self, settings: Settings, use_default_db_connection=False) -> None:
        super().__init__()
        self.settings = settings
        self.use_default_db_connection = use_default_db_connection

    def make_send(
        self, notification: DjangoProjectBaseNotification, extra_data, resend=False
    ) -> DjangoProjectBaseNotification:
        # TODO: THIS SHOULD BE CALLED ONLY FROM CELERY BACKGROUND TASK

        sent_channels: list = []
        failed_channels: list = []
        db_name = NOTIFICATION_QUEUE_NAME if not self.use_default_db_connection else "default"

        exceptions = ""
        from django_project_base.licensing.logic import LogAccessService

        if notification.required_channels is None:
            return notification
        already_sent_channels = set(
            filter(
                lambda i: i not in (None, "") and i,
                notification.sent_channels.split(",") if notification.sent_channels else [],
            )
        )
        required_channels = set(
            filter(
                lambda i: i not in (None, "") and i,
                notification.required_channels.split(",") if notification.required_channels else [],
            )
        ) - (already_sent_channels if not resend else set())
        already_failed_channels = set(
            filter(
                lambda i: i not in (None, "") and i,
                notification.failed_channels.split(",") if notification.failed_channels else [],
            )
        )

        from django_project_base.notifications.base.channels.sms_channel import SmsChannel

        if notification.send_notification_sms:
            required_channels.add(SmsChannel.name)

        for channel_identifier in required_channels:
            channel = ChannelIdentifier.channel(
                channel_identifier,
                settings=self.settings,
                project_slug=notification.project_slug,
                ensure_dlr_user=False,
            )
            try:
                # check license
                any_sent = LogAccessService(db=db_name).log(
                    user_profile_pk=notification.user,
                    notifications_channels_state=sent_channels,
                    record=notification,
                    item_price=channel.notification_price,
                    comment=str(channel),
                    on_sucess=lambda: channel.send(
                        notification=notification, extra_data=extra_data, settings=self.settings
                    ),
                    is_system_notification=extra_data.get("is_system_notification"),
                    sender=channel.sender(notification),
                )
                sent_channels.append(channel) if any_sent > 0 else failed_channels.append(channel)
            except Exception as e:
                logging.getLogger(__name__).error(e)
                failed_channels.append(channel)
                exceptions += f"{str(e)}\n\n"

        if notification.created_at:
            if required_channels:
                notification.sent_channels = (
                    ",".join(
                        set(
                            list(
                                map(
                                    lambda f: str(f),
                                    filter(
                                        lambda d: d is not None,
                                        map(lambda c: c.name, sent_channels),
                                    ),
                                )
                            )
                            + list(already_sent_channels)
                        )
                    )
                    if sent_channels
                    else ",".join(already_sent_channels)
                )
            notification.failed_channels = (
                ",".join(
                    set(
                        list(
                            map(
                                lambda f: str(f),
                                filter(
                                    lambda d: d is not None,
                                    map(lambda c: c.name, failed_channels),
                                ),
                            )
                        )
                        + list(already_failed_channels)
                    )
                )
                if failed_channels
                else ",".join(already_failed_channels)
            )
            notification.sent_at = timezone.now().timestamp() if notification.sent_channels else None
            notification.exceptions = exceptions if exceptions else None

            _req = notification.required_channels.split(",") if notification.required_channels else []
            _snt = notification.sent_channels.split(",") if notification.sent_channels else []
            if set(_snt) == set(_req):
                notification.failed_channels = ""

            _fld = notification.failed_channels.split(",") if notification.failed_channels else []

            notification.done = set(_req).issubset(set(_snt) | set(_fld))

            notification.save(
                update_fields=[
                    "sent_at",
                    "sent_channels",
                    "failed_channels",
                    "exceptions",
                    "done",
                ],
                using=db_name,
            )
        return notification
