import datetime
import uuid

import swapper
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.validators import int_list_validator
from django.db import models
from django.db.models import SET_NULL, Value
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _

from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.notification_queryset import NotificationQuerySet


class AbstractDjangoProjectBaseMessage(models.Model):
    PLAIN_TEXT = "text/plain"
    HTML = "text/html"

    CONTENT_TYPE_CHOICES = ((PLAIN_TEXT, "Plain text"), (HTML, "Html"))

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, verbose_name=_("Id"))
    subject = models.TextField(null=True, blank=True, verbose_name=_("Subject"))
    body = models.TextField(verbose_name=_("Body"))
    footer = models.TextField(null=True, blank=True, verbose_name=_("Footer"))
    content_type = models.CharField(null=False, choices=CONTENT_TYPE_CHOICES, default=PLAIN_TEXT, max_length=64)

    class Meta:
        abstract = True


class DjangoProjectBaseMessage(AbstractDjangoProjectBaseMessage):
    pass


def integer_ts():
    return int(datetime.datetime.now().timestamp())


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
    created_at = models.BigIntegerField(default=integer_ts, editable=False, verbose_name=_("Created at"))
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
    counter = models.SmallIntegerField(default=1)

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


class SearchItemObject:
    label = ""

    def __init__(self, dict_val):
        for key, value in dict_val.items():
            setattr(self, key, value)
        setattr(self, "pk", dict_val["ido"])
        setattr(self, "id", dict_val["ido"])

    def __str__(self) -> str:
        return self.label


class SearchItemsManager(models.Manager):
    user_model_content_type_id = ContentType.objects.get_for_model(get_user_model()).pk

    def get_queryset(self):
        tag_model = swapper.load_model("django_project_base", "Tag")
        tag_model_content_type_id = ContentType.objects.get_for_model(tag_model).pk
        qs = []
        qs += [
            SearchItemObject(o)
            for o in get_user_model()  # qs users
            .objects.annotate(
                ido=Concat(get_user_model()._meta.pk.name, Value("-"), Value(self.user_model_content_type_id))
            )
            .extra(
                select={
                    "object_id": get_user_model()._meta.pk.name,
                    "label": "username",
                    "content_type_id": self.user_model_content_type_id,
                }
            )
            .values("object_id", "label", "content_type_id", "ido")
        ]
        qs += [
            SearchItemObject(o)
            for o in tag_model.objects.annotate(  # qs tags
                ido=Concat(tag_model._meta.pk.name, Value("-"), Value(tag_model_content_type_id))
            )
            .extra(
                select={
                    "object_id": tag_model._meta.pk.name,
                    "label": "name",
                    "content_type_id": tag_model_content_type_id,
                }
            )
            .values("object_id", "label", "content_type_id", "ido")
        ]
        return qs


class SearchItems(models.Model):
    objects = SearchItemsManager()

    content_type_id = models.PositiveIntegerField()
    object_id = models.PositiveBigIntegerField()
    name = models.CharField(max_length=256)
    id = models.PositiveBigIntegerField(primary_key=True)

    class Meta:
        abstract = False
        managed = False
        db_table = "search-items-table"
