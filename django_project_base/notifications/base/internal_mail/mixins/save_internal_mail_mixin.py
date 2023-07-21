import json
import socket

from django.db.models import QuerySet, Q
from django.db.models.functions import Length
from django.urls import reverse
from django.utils import timezone

from main.rest_df.internal_mail.config import MAIL_AGGREGATION_TIMEDELTA, INTERNAL_MAIL_LENGTH_SIMILARITY_BUFFER_VALUE
from mars.settings import DEPLOY_MAIN


class SaveInternalMailMixin(object):
    """Mixin class with extra functionalities for InternalMail model save method"""

    def handle_similar_emails(self) -> bool:
        """
        Determines which mails are duplicates
        :return: True if new mail is duplicate
        """
        from main.models import InternalMail
        message_length: int = len(self.message)
        same_emails: QuerySet = InternalMail.objects.using('message_store_read').annotate(
            message_len=Length('message')
        ).filter(
            title=self.title,
            recipients=self.recipients,
            sender=self.sender,
            created_at__gt=timezone.now() - MAIL_AGGREGATION_TIMEDELTA,
            message_len__gte=message_length - INTERNAL_MAIL_LENGTH_SIMILARITY_BUFFER_VALUE,
            message_len__lte=message_length + INTERNAL_MAIL_LENGTH_SIMILARITY_BUFFER_VALUE,
            origin_server=socket.gethostname().lower(),
            report_sent_at__isnull=True,
            reports__isnull=True,
            mail_content_entity_context=json.dumps(self.mail_content_entity_context),
        ).order_by('-created_at')
        # todo: install trigram extension to find similar mails that were created in a burst
        if same_emails.exists():
            first_same_email: InternalMail = same_emails.first()
            InternalMail.objects.using(
                'message_store_read'
            ).filter(pk=first_same_email.pk).update(
                counter=first_same_email.counter + 1,
                counter_updated_at=timezone.now(),
            )
            first_same_email.refresh_from_db(using='message_store_read')
            from main.rest_df.internal_mail.commands.report_email_duplicates_command import ReportEmailDuplicatesCommand
            ReportEmailDuplicatesCommand(first_same_email).execute()
            return True
        return False

    def notify_users_that_new_mail_was_sent(self):
        """
        Notify suitable users that new mail was created
        """
        if not DEPLOY_MAIN:
            from main.models import MessagesStore
            link_to_internal_mail_dashboard: str = reverse('internal-mail-dashboard')
            for recipient in self.recipients:
                from django.contrib.auth import get_user_model
                user_filter: QuerySet = get_user_model().objects.filter(email=recipient).filter(
                    Q(is_staff=True) | Q(is_superuser=True))
                for user in user_filter:
                    MessagesStore(user_id=user.id, level=MessagesStore.WARNING,
                                  message='<p>'
                                          'You received an internal mail message. '
                                          'Please click on View messages button to view it'
                                          '<input name="internal-message-notification" style="display: none;">'
                                          '</p>',
                                  buttons=json.dumps([dict(name='View messages', link=link_to_internal_mail_dashboard,
                                                           title='Importing device data', link_type='href'),
                                                      dict(name='Cancel', link='javascript.void();',
                                                           title='Importing device data')])).save(
                        using='message_store_read')
