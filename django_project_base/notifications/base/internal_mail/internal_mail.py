import datetime
import socket

from django.core.validators import validate_email
from django.utils import timezone

from main.models import InternalMail as InternalMailModel
from main.rest_df.internal_mail.services.send_internal_mail_service import SendInternalMailService


class InternalMail(object):
    """InternalMail Api object. This class serves as a bluprint for concrete mail objects"""

    def __init__(self, title: str, message: str, recipients: list, sender: str,
                 report_sent_at: int or None = None, parent_mail: InternalMailModel or None = None,
                 mail_content_entity_context: dict = {}) -> None:
        """
        InternalMail initialization
        :param origin_server: Mail origin server name
        :param title: Mail subject
        :param message: Mail message
        :param recipients: Mail recepients
        :param sender: Mail sender
        """
        self.title = title
        self.message = message
        self.recipients = recipients
        self.sender = sender
        self.origin_server = socket.gethostname().lower()
        self.created_at = timezone.now()
        self.report_sent_at = report_sent_at
        self.parent_mail = parent_mail
        self.mail_content_entity_context = mail_content_entity_context
        self.validate()

    def validate(self) -> None:
        """InternalMail object validation"""
        assert isinstance(self.title, str) and self.title, "Title must be non empty string"
        assert isinstance(self.message, str) and self.message, "Message must be non empty string"
        assert isinstance(self.sender, str) and self.sender, "Sender must be non empty string"
        assert isinstance(self.origin_server, str) and self.origin_server, "Origin server must be non empty string"
        validate_email(self.sender)
        assert isinstance(self.recipients, list) and self.recipients, "Recipients must be non empty list"
        assert isinstance(self.created_at,
                          datetime.datetime) and self.created_at, "Created at must be datetime instance"

    def send(self) -> None or object:
        """
        Simulate mail send

        If mail should be sent to real mail server, True is returned. This means new record was created.
        """
        return SendInternalMailService().send(self)
