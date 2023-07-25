import datetime
import os
import pathlib
from typing import List

from django.conf import settings
from django.utils.module_loading import import_string

from django_project_base.notifications.base.channels.channel import Channel
from django_project_base.notifications.base.enums import ChannelIdentifier

email_service_blocked_ck: str = "email_service_blocked"


class MailChannel(Channel):
    id = ChannelIdentifier.MAIL.value

    name = "e-mail"

    provider = import_string(getattr(settings, "EMAIL_PROVIDER", ""))

    @staticmethod
    def __make_send_mail(notification: "DjangoProjectBaseNotification", extra_data) -> int:  # noqa: F821
        recipients: List[int] = notification.recipients
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
        recipients: List[int] = notification.recipients
        res_count = len(recipients)
        if os.path.exists("/tmp/uwsgi.socket"):
            # check if server was restarted, if it was just discard messages
            file_p: pathlib.Path = pathlib.Path("/tmp/uwsgi.socket")
            mtime: float = datetime.datetime.fromtimestamp(file_p.stat().st_mtime, tz=datetime.timezone.utc).timestamp()
            if datetime.datetime.now().timestamp() - mtime < settings.MAIL_TIMEOUT_AFTER_WSGI_RESTART:
                return res_count

        with open("/tmp/not.txt", "a") as f:
            f.write(f"\n{recipients} dfgAAAAdfgdg\n")

        if not recipients:
            return 0

        # if kwargs.get("force_send", False): TODO
        return MailChannel.__make_send_mail(notification, extra_data)

        # if notification.persist:
        #     try:
        #         # TODO
        #
        #         number_of_sent_emails: int = MailChannel.__make_send_mail(notification)
        #         internal_email_saved.sent_at = timezone.now()
        #         internal_email_saved.save(update_fields=["sent_at"], action="save")
        #         return number_of_sent_emails
        #     except Exception as exc:
        #         exception_msg: str = str(exc)
        #         internal_email_saved.mail_server_exception = exception_msg
        #         internal_email_saved.save(update_fields=["mail_server_exception"], action="save")
        #         # notify admin that mail service is blocked
        #         admin_notified: Optional[float] = cache.get(email_service_blocked_ck)
        #         if (
        #             "Unusual sending activity detected".lower() in exception_msg.lower()
        #             and (not admin_notified or time.time() - admin_notified > 5400)
        #             and settings.EMAIL_BLOCKED_SMS_NOTIFICATION_RECIPIENT
        #         ):
        #             # notification can be sent only once every 90 mins
        #             cache.set(email_service_blocked_ck, time.time(), timeout=None)

        # TODO: WHEN SMS SERVICE IS INTEGRATED NOTIFY ADMIN

        # sms_service: MakeRequestForNexmoProviderService = MakeRequestForNexmoProviderService()
        # sms_service.send_sms(
        #     **{
        #         "sender": sms_service.sender_phone_number,
        #         "recipient": settings.EMAIL_BLOCKED_SMS_NOTIFICATION_RECIPIENT,
        #         "body": (
        #             "Mars email server blocked error. Please unblock server. Error: %s" % exception_msg
        #         ),
        #     }
        # )
        # return 0
