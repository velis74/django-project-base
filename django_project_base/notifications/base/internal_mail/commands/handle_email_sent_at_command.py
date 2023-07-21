from django.utils import timezone

from main.rest_df.internal_mail.commands.internal_email_command import InternalEmailCommand
from main.logic.mars_mail_message import MarsMailMessage
from main.models import InternalMail as InternalMailModel
from main.rest_df.internal_mail.commands.internal_mail_service_commands_mixin import InternalMailServiceCommandsMixin


class HandleEmailSentAtCommand(InternalMailServiceCommandsMixin, InternalEmailCommand):

    def __init__(self, command_payload: InternalMailModel) -> None:
        assert isinstance(command_payload, InternalMailModel)
        super().__init__(command_payload)

    def execute(self) -> None:
        internal_mail_object: InternalMailModel = self.payload
        if internal_mail_object.sent_at:
            return None

        email_message: MarsMailMessage = MarsMailMessage(
            subject=internal_mail_object.title,
            body=self._prepare_message(internal_mail_object),
            from_email=internal_mail_object.sender,
            to=internal_mail_object.recipients.split(','),
        )
        try:
            self._send_without_internal_email_service(email_message)
            internal_mail_object.sent_at = timezone.now()
            internal_mail_object.save(action='save', update_fields=['sent_at'])
        except Exception as exc:
            internal_mail_object.mail_server_exception = str(exc)
            internal_mail_object.save(update_fields=['mail_server_exception'], action='save')
