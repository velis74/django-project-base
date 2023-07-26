from typing import List

from django.conf import settings
from django.utils.module_loading import import_string

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier


class MailChannel(Channel):
    id = ChannelIdentifier.MAIL.value

    name = "e-mail"

    provider = import_string(getattr(settings, "EMAIL_PROVIDER", ""))

    @staticmethod
    def __make_send_mail(notification: "DjangoProjectBaseNotification", extra_data) -> int:  # noqa: F821
        recipients: List[int] = list(map(int, notification.recipients.split(","))) if notification.recipients else []
        res_count = len(recipients)
        MailChannel.provider().send(notification=notification, extra_data=extra_data)
        return res_count

    @staticmethod
    def send(notification: "DjangoProjectBaseNotification", extra_data, **kwargs) -> int:  # noqa: F821
        """
        Overrides default send email messages

        :param fail_silently:
        :return: number of sent messages
        """
        recipients: List[int] = list(map(int, notification.recipients.split(","))) if notification.recipients else []
        if not recipients:
            return 0

        return MailChannel.__make_send_mail(notification, extra_data)
