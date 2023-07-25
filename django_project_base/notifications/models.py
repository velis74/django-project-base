import uuid

from django.core.validators import int_list_validator
from django.db import models
from django.db.models import SET_NULL
from django.utils.translation import gettext_lazy as _

from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.notification_queryset import NotificationQuerySet
from django_project_base.notifications.utils import utc_now


class AbstractDjangoProjectBaseMessage(models.Model):
    PLAIN_TEXT = "text/plain"
    HTML = "text/html"

    CONTENT_TYPE_CHOICES = ((PLAIN_TEXT, "Plain text"), (HTML, "Html"))

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, verbose_name=_("Id"))
    subject = models.TextField(null=True, blank=True, verbose_name=_("Subject"))
    body = models.TextField(null=False, blank=False, verbose_name=_("Body"))
    footer = models.TextField(null=True, blank=True, verbose_name=_("Footer"))
    content_type = models.CharField(null=False, choices=CONTENT_TYPE_CHOICES, default=PLAIN_TEXT, max_length=64)

    class Meta:
        abstract = True


class DjangoProjectBaseMessage(AbstractDjangoProjectBaseMessage):
    pass


class AbstractDjangoProjectBaseNotification(models.Model):
    locale = models.CharField(null=True, blank=True, max_length=8, verbose_name=_("Locale"))
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, verbose_name=_("Id"))
    level = models.CharField(
        null=False,
        blank=False,
        max_length=16,
        choices=[(i.value, i.name.lower().title()) for i in NotificationLevel],
        verbose_name=_("Level"),
    )
    required_channels = models.CharField(null=True, blank=True, max_length=32, verbose_name=_("Required channels"))
    sent_channels = models.CharField(null=True, blank=True, max_length=32, verbose_name=_("Sent channels"))
    failed_channels = models.CharField(null=True, blank=True, max_length=32, verbose_name=_("Failed channels"))
    created_at = models.BigIntegerField(
        default=lambda: int(utc_now().timestamp()), editable=False, verbose_name=_("Created at")
    )
    sent_at = models.BigIntegerField(null=True, blank=True, verbose_name=_("Sent at"))
    delayed_to = models.BigIntegerField(null=True, blank=True, verbose_name=_("Delayed to"))
    type = models.CharField(
        null=False,
        blank=False,
        max_length=16,
        choices=[(i.value, i.name.lower().title()) for i in NotificationType],
        default=NotificationType.STANDARD.value,
        verbose_name=_("Type"),
    )
    recipients = models.CharField(blank=False, null=True, max_length=2048, validators=[int_list_validator])
    message = models.OneToOneField(DjangoProjectBaseMessage, on_delete=SET_NULL, null=True, verbose_name=_("Message"))
    exceptions = models.TextField(null=True)
    content_entity_context = models.TextField()
    counter = models.SmallIntegerField(default=0)

    class Meta:
        abstract = True


class DjangoProjectBaseNotification(AbstractDjangoProjectBaseNotification):
    objects = NotificationQuerySet.as_manager()

    _recipients_list = []

    def _get_recipients(self):
        return self._recipients_list

    def _set_recipents(self, val):
        self._recipients_list = val

    recipients_list = property(_get_recipients, _set_recipents)
