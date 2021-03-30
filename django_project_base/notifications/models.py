import uuid

from django.conf import settings
from django.db import models
from django.db.models import SET_NULL

from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.notification_queryset import NotificationQuerySet
from django_project_base.notifications.utils import _utc_now


class AbstractDjangoProjectBaseMessage(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    subject = models.TextField(null=True, blank=True)
    body = models.TextField(null=False, blank=False)
    footer = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class DjangoProjectBaseMessage(AbstractDjangoProjectBaseMessage):
    pass


class AbstractDjangoProjectBaseNotification(models.Model):
    locale = models.CharField(null=True, blank=True, max_length=8)
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    level = models.CharField(null=False, blank=False, max_length=16, choices=[
        (i.value, i.name.lower().title()) for i in NotificationLevel])
    required_channels = models.CharField(null=True, blank=True, max_length=32)
    sent_channels = models.CharField(null=True, blank=True, max_length=32)
    failed_channels = models.CharField(null=True, blank=True, max_length=32)
    created_at = models.DateTimeField(default=_utc_now, editable=False, blank=False, null=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    delayed_to = models.DateTimeField(null=True, blank=True)
    type = models.CharField(null=False, blank=False, max_length=16, choices=[
        (i.value, i.name.lower().title()) for i in NotificationType], default=NotificationType.STANDARD.value)
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='notifications',
    )
    message = models.OneToOneField(DjangoProjectBaseMessage, on_delete=SET_NULL, null=True)

    class Meta:
        abstract = True


class DjangoProjectBaseNotification(AbstractDjangoProjectBaseNotification):
    objects = NotificationQuerySet.as_manager()
