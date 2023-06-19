from django.core.mail import send_mail

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier


class MailChannel(Channel):
    id = ChannelIdentifier.MAIL.value

    @staticmethod
    def send(notification: "Notification") -> None:  # noqa: F821
        from django_project_base.notifications.models import DjangoProjectBaseMessage

        send_mail(
            subject=notification.message.subject,
            message=notification.message.body,
            from_email="",
            recipient_list=notification._recipients,
            html_message=notification.message.body
            if notification.message.content_type == DjangoProjectBaseMessage.HTML
            else None,
        )
