from django.conf import settings
from django.utils.module_loading import import_string

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier


class MailChannel(Channel):
    id = ChannelIdentifier.MAIL.value

    provider = import_string(getattr(settings, "EMAIL_PROVIDER", ""))

    @staticmethod
    def send(notification: "Notification") -> None:  # noqa: F821
        MailChannel.provider().send(notification=notification)
