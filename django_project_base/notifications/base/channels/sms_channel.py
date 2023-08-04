from django.conf import settings
from django.utils.module_loading import import_string

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier


class SmsChannel(Channel):
    id = ChannelIdentifier.SMS.value

    name = "SMS"

    provider = None

    @staticmethod
    def send(notification: "DjangoProjectBaseNotification", extra_data, **kwargs) -> int:  # noqa: F821
        raise NotImplementedError
