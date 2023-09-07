from typing import List

from django.conf import settings

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier


class MailChannel(Channel):
    id = ChannelIdentifier.MAIL.value

    name = "EMail"

    notification_price = 0.0002  # TODO get from settings

    provider_setting_name = "EMAIL_PROVIDER"

    @staticmethod
    def __make_send_mail(notification: "DjangoProjectBaseNotification", extra_data) -> int:  # noqa: F821
        if getattr(settings, "TESTING", False):
            recipients: List[int] = (
                list(map(int, notification.recipients.split(","))) if notification.recipients else []
            )
            return len(recipients)
        return MailChannel.provider(extra_settings=extra_data, setting_name=MailChannel.provider_setting_name).send(
            notification=notification, extra_data=extra_data
        )

    @staticmethod
    def send(notification: "DjangoProjectBaseNotification", extra_data, **kwargs) -> int:  # noqa: F821
        """
        Overrides default send email messages

        :param fail_silently:
        :return: number of sent messages
        """
        return MailChannel.__make_send_mail(notification, extra_data)
