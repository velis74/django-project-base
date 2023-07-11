import datetime
import uuid

from django.conf import settings
from django.db import models
from django.db.models import SET_NULL
from django.utils.translation import gettext_lazy as _

from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.notification_queryset import NotificationQuerySet
from django_project_base.notifications.utils import utc_now


class AbstractDjangoProjectBaseMessage(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, verbose_name=_("Id"))
    subject = models.TextField(null=True, blank=True, verbose_name=_("Subject"))
    body = models.TextField(null=False, blank=False, verbose_name=_("Body"))
    footer = models.TextField(null=True, blank=True, verbose_name=_("Footer"))

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
    created_at = models.DateTimeField(
        default=utc_now, editable=False, blank=False, null=False, verbose_name=_("Created at")
    )
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Sent at"))
    delayed_to = models.DateTimeField(null=True, blank=True, verbose_name=_("Delayed to"))
    type = models.CharField(
        null=False,
        blank=False,
        max_length=16,
        choices=[(i.value, i.name.lower().title()) for i in NotificationType],
        default=NotificationType.STANDARD.value,
        verbose_name=_("Type"),
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="notifications", verbose_name=_("Recipients")
    )
    message = models.OneToOneField(DjangoProjectBaseMessage, on_delete=SET_NULL, null=True, verbose_name=_("Message"))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.delayed_to = (
            self.delayed_to.replace(tzinfo=datetime.timezone.utc)
            if self.delayed_to and self.delayed_to.tzinfo != datetime.timezone.utc
            else self.delayed_to
        )
        self.created_at = (
            self.created_at.replace(tzinfo=datetime.timezone.utc)
            if self.created_at and self.created_at.tzinfo != datetime.timezone.utc
            else self.created_at
        )

        self.sent_at = (
            self.sent_at.replace(tzinfo=datetime.timezone.utc)
            if self.sent_at and self.sent_at.tzinfo != datetime.timezone.utc
            else self.sent_at
        )

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        abstract = True


class DjangoProjectBaseNotification(AbstractDjangoProjectBaseNotification):
    objects = NotificationQuerySet.as_manager()
