import abc

from main.models import InternalMail


class SaveToInternalMailStorageServiceBase(abc.ABC):
    """Base class for saving InternalMail(main/internal_mail/internal_mail.py)
    object to storage
    """

    @abc.abstractmethod
    def save(self, email_data: dict) -> None or object:
        """Default save method"""
        return InternalMail(**email_data).save()
