from django.core.mail import send_mail

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier


class MailChannel(Channel):
    id = ChannelIdentifier.MAIL.value

    @staticmethod
    def send(notification: "Notification") -> None:  # noqa: F821
        # def send_mail(
        #         subject,
        #         message,
        #         from_email,
        #         recipient_list,
        #         fail_silently=False,
        #         auth_user=None,
        #         auth_password=None,
        #         connection=None,
        #         html_message=None,
        # ):

        send_mail()
