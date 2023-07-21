from django.utils.translation import gettext as __

from main.logic.mars_mail_message import MarsMailMessage
from main.models import InternalMail as InternalMailModel


class InternalMailServiceCommandsMixin(object):

    def _prepare_message(self, mail_object: InternalMailModel) -> str:
        message = mail_object.message
        if mail_object.counter > 1:
            message = '\n' + __('Number of times this email occurred:') + ' %d' % mail_object.counter + \
                      '\n\n' + message
        return message

    def __make_send(self, mail_object: MarsMailMessage, force_send=False) -> int:
        assert isinstance(mail_object, MarsMailMessage)
        mail_object.content_subtype = 'html'
        mail_object.encoding = 'UTF-8'
        return mail_object.send(force_send=force_send)

    def _send_without_internal_email_service(self, mail_object: MarsMailMessage) -> int:
        return self.__make_send(mail_object, force_send=True)

    def _send_with_internal_mail_service(self, mail_object: MarsMailMessage) -> int:
        return self.__make_send(mail_object, force_send=False)
