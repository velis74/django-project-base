import datetime
import types
import uuid

import swapper

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.validators import int_list_validator
from django.db import models, OperationalError, ProgrammingError, transaction
from django.db.models import SET_NULL, Value
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _

from django_project_base.notifications.base.enums import NotificationLevel, NotificationType
from django_project_base.notifications.notification_queryset import NotificationQuerySet
from django_project_base.utils import get_pk_name, IntDescribedEnum


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
        verbose_name = "Message"


class DjangoProjectBaseMessage(AbstractDjangoProjectBaseMessage):
    _unsaved_attachments = []

    def __init__(self, *args, **kwargs):
        attachments = kwargs.pop("attachments", None)
        super().__init__(*args, **kwargs)
        if attachments:
            if not isinstance(attachments, (list, tuple, set, types.GeneratorType)):
                attachments = [attachments]
            for attachment in attachments:
                self._unsaved_attachments.append(DjangoProjectBaseMessageAttachment(message=self, file=attachment))

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        for attachment in self.get_unsaved_attachments():
            attachment.save()

    def get_unsaved_attachments(self):
        return self._unsaved_attachments

    def get_attachments(self):
        if not self._state.adding:
            return list(self.attachments.all())
        else:
            return self.get_unsaved_attachments()


class AbstractDjangoProjectBaseMessageAttachment(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, verbose_name=_("Id"))
    file = models.FileField(null=False, blank=False, verbose_name=_("Attachment"))

    class Meta:
        abstract = True
        verbose_name = "MessageAttachment"


class DjangoProjectBaseMessageAttachment(AbstractDjangoProjectBaseMessageAttachment):
    message = models.ForeignKey(
        DjangoProjectBaseMessage, on_delete=models.CASCADE, verbose_name=_("Message"), related_name="attachments"
    )
    pass


def integer_ts():
    return int(datetime.datetime.now().timestamp())


class AbstractDjangoProjectBaseNotification(models.Model):
    DELAYED_INDEFINITELY = 2**63 - 1  # Max bigint

    locale = models.CharField(null=True, blank=True, max_length=8, verbose_name=_("Locale"))  # language
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
    message = models.OneToOneField(
        DjangoProjectBaseMessage,
        on_delete=SET_NULL,
        null=True,
        verbose_name=_("Message"),
    )
    exceptions = models.TextField(null=True)
    content_entity_context = models.TextField()
    counter = models.SmallIntegerField(default=1)
    recipients_original_payload = models.CharField(blank=False, null=False, max_length=2048)
    recipients_original_payload_search = models.TextField(blank=False, null=True, db_index=True)
    project_slug = models.CharField(null=True, blank=True, max_length=1024)
    send_notification_sms = models.BooleanField(null=False, blank=False, default=False)
    send_notification_sms_text = models.TextField(blank=False, null=True)
    extra_data = models.JSONField(null=True, blank=False)
    done = models.BooleanField(default=False)

    class Meta:
        abstract = True
        verbose_name = "Notification"
        indexes = [
            models.Index(fields=["delayed_to", "done"]),
        ]


class DjangoProjectBaseNotification(AbstractDjangoProjectBaseNotification):
    objects = NotificationQuerySet.as_manager()

    _recipients_list = []
    _user = None
    _sender = {}
    _email_list = []
    _email_fallback = False

    def _get_recipients(self):
        return self._recipients_list

    def _set_recipents(self, val):
        self._recipients_list = val

    def _get_user(self):
        return self._user

    def _set_user(self, val):
        self._user = val

    def _get_sender(self):
        return self._sender

    def _set_sender(self, val):
        self._sender = val

    def _get_email_list(self):
        return self._email_list

    def _set_email_list(self, val):
        self._email_list = val

    def _get_email_fallback(self):
        return self._email_fallback

    def _set_email_fallback(self, val):
        self._email_fallback = val

    recipients_list = property(_get_recipients, _set_recipents)

    user = property(_get_user, _set_user)

    sender = property(_get_sender, _set_sender)

    email_list = property(_get_email_list, _set_email_list)

    email_fallback = property(_get_email_fallback, _set_email_fallback)

    @property
    def recipients_raw(self):
        ids = [int(recipients_id) for recipients_id in self.recipients.split(",")] if self.recipients else []
        return swapper.load_model("django_project_base", "Profile").objects.filter(id__in=ids)

    @property
    def is_delayed(self):
        return self.delayed_to and self.delayed_to > datetime.datetime.now().timestamp()

    def prepare_for_send(self, user_pk=None):
        from django_project_base.notifications.base.notification import Notification

        self.sender = Notification._get_sender_config(self.project_slug)
        self.user = (self.extra_data or {}).get("user") or user_pk
        rec_list = []
        for usr in self.recipients.split(","):
            rec_list.append(
                {
                    k: v
                    for k, v in get_user_model().objects.get(pk=usr).userprofile.__dict__.items()
                    if not k.startswith("_")
                }
            )
        self.recipients_list = rec_list

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        self.__class__.objects.invalidate_cache(self.pk)

    def delete(self, using=None, keep_parents=False):
        pk = self.pk
        ret = super().delete(using, keep_parents)
        self.__class__.objects.invalidate_cache(pk)
        return ret


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
    def get_queryset(self, **kwargs):
        from django_project_base.account.rest.project_profiles_utils import annotate_with_full_name

        # qs rabim zato, ker pri inicializaciji swagerja koda hoče imeti queryset.model... kar pa list seveda nima.
        # Zato namesto praznih listov vrnem qs.none()
        qs = super().get_queryset()
        tag_model = swapper.load_model("django_project_base", "Tag")

        slug = ""

        if not kwargs.get("request"):
            try:
                from django_project_base.base.middleware import get_current_request

                request = get_current_request()
                if request and getattr(request, "selected_project_slug", None):
                    slug = request.selected_project_slug
            except Exception:
                pass
        else:
            slug = getattr(kwargs["request"], "selected_project_slug", "")

        if not slug:
            return qs.none()

        try:
            tag_model_content_type_id = ContentType.objects.get_for_model(tag_model).pk
            user_model_content_type_id = ContentType.objects.get_for_model(get_user_model()).pk
            user_model = get_user_model()
            user_qs = (
                user_model.objects.filter(userprofile__projects__project__slug=slug)
                .distinct()
                .annotate(  # qs users
                    ido=Concat(
                        get_pk_name(user_model),
                        Value("-"),
                        Value(user_model_content_type_id),
                        output_field=models.CharField(),
                    )
                )
                .exclude(is_active=False)
                .extra(
                    select={
                        "object_id": f"{user_model._meta.db_table}.{get_pk_name(user_model)}",
                        "content_type_id": user_model_content_type_id,
                    }
                )
            )
            user_qs = (
                annotate_with_full_name(user_qs, "label")
                .values("object_id", "label", "content_type_id", "ido")
                .order_by("label")
            )

            qs = []
            qs += [SearchItemObject(o) for o in user_qs]
            tgs = [
                SearchItemObject(o)
                for o in tag_model.objects.filter(project__slug=slug)
                .distinct()
                .annotate(  # qs tags
                    ido=Concat(
                        get_pk_name(tag_model),
                        Value("-"),
                        Value(tag_model_content_type_id),
                        output_field=models.CharField(),
                    )
                )
                .extra(
                    select={
                        "object_id": f"{tag_model._meta.db_table}.{get_pk_name(tag_model)}",
                        "label": f"{tag_model._meta.db_table}.name",
                        "content_type_id": tag_model_content_type_id,
                    }
                )
                .values("object_id", "label", "content_type_id", "ido")
                .order_by("label")
            ]
            qs += tgs
            return qs
        except OperationalError:
            return qs.none()
        except ProgrammingError:
            return qs.none()


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


class DeliveryReport(models.Model):
    class Status(IntDescribedEnum):
        DELIVERED = 1, _("Delivered")
        NOT_DELIVERED = 2, _("Not Delivered")
        PENDING_DELIVERY = 3, _("Pending delivery")

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, verbose_name=_("Id"), db_index=True)
    notification = models.ForeignKey(DjangoProjectBaseNotification, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=1024, db_index=True, null=False, blank=False)
    channel = models.CharField(max_length=1024, null=False, blank=False)
    provider = models.CharField(max_length=1024, db_index=True, null=False, blank=False)
    payload = models.JSONField(null=True, blank=False)
    status = models.IntegerField(
        default=Status.PENDING_DELIVERY, choices=Status.get_choices_tuple(), db_index=True, null=False
    )
    auxiliary_notification = models.UUIDField(verbose_name=_("Auxiliary notification"), null=True, blank=False)
