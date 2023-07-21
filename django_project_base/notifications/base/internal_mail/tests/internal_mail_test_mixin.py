from main.logic.mars_mail_message import MarsMailMessage
from mars.settings import API_DOCS_ADMIN_EMAIL


class InternalMailTestMixin(object):

    def create_mars_message_object(self) -> MarsMailMessage:
        return MarsMailMessage(
            subject='Test mail',
            body='content',
            from_email=API_DOCS_ADMIN_EMAIL,
            to=[API_DOCS_ADMIN_EMAIL, ],
        )
