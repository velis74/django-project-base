from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier


class MailChannel(Channel):
    id = ChannelIdentifier.MAIL.value

    @staticmethod
    def send(notification: 'Notification') -> None:
        print('send mail')
