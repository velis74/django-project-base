from typing import Type

from main.rest_df.internal_mail.services.save_to_internal_mail_storage_service import SaveToInternalMailStorageService
from main.rest_df.internal_mail.services.save_to_internal_mail_storage_service_base import \
    SaveToInternalMailStorageServiceBase


class SendInternalMailService:
    """Service for sending InternalMail(main/internal_mail/internal_mail.py)"""

    @staticmethod
    def __get_send_service() -> Type[SaveToInternalMailStorageServiceBase]:
        """Returns appropriate service for sending mail"""
        return SaveToInternalMailStorageService

    def send(self, email) -> None or object:
        """
        Sends mail
        :param email: InternalMail(main/internal_mail/internal_mail.py)
        :return: Number of emails sent
        """
        from main.rest_df.internal_mail.internal_mail import InternalMail
        assert isinstance(email, InternalMail)
        return self.__get_send_service()().save(email.__dict__)
