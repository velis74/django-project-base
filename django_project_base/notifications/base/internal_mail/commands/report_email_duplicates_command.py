import copy
import math

from django.utils.translation import gettext as __
from main.rest_df.internal_mail.commands.internal_email_command import InternalEmailCommand
from main.logic.mars_mail_message import MarsMailMessage
from main.models import InternalMail as InternalMailModel
from main.rest_df.internal_mail.commands.internal_mail_service_commands_mixin import InternalMailServiceCommandsMixin
from main.rest_df.internal_mail.config import INTERNAL_MAIL_CHECKING_REPORT_INTERVALS_IN_MINUTES
from mars import settings


class ReportEmailDuplicatesCommand(InternalMailServiceCommandsMixin, InternalEmailCommand):

    def __init__(self, command_payload: InternalMailModel) -> None:
        assert isinstance(command_payload, InternalMailModel)
        super().__init__(command_payload)

    def __send_report(self, email_object: InternalMailModel, time_limit: int):
        report_email_message: MarsMailMessage = MarsMailMessage(
            subject='%s - %s' % (email_object.title,
                                 __('Simultaneous emails report after:' + ' %d minutes' % time_limit)),
            body=self._prepare_message(email_object),
            from_email=email_object.sender,
            to=settings.SYSTEM_DEVELOPER_EMAILS,
            report_sent_at=time_limit,
            parent_mail=email_object,
        )
        self._send_with_internal_mail_service(report_email_message)

    def execute(self) -> None:
        if self.payload.counter > 1:
            counter_updated_at_vs_mail_created_time_diff_in_min: int = abs(math.floor(
                (self.payload.counter_updated_at - self.payload.created_at).total_seconds() / 60))
            intervals: list = copy.copy(INTERNAL_MAIL_CHECKING_REPORT_INTERVALS_IN_MINUTES)
            intervals.sort()
            for time_limit in intervals:
                if (counter_updated_at_vs_mail_created_time_diff_in_min > time_limit and not
                self.payload.reports.filter(report_sent_at=time_limit).exists()):
                    self.__send_report(self.payload, time_limit)
