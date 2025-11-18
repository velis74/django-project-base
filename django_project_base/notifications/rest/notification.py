import datetime
import json
import time

from typing import List, Optional

import pytz
import swapper

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import transaction
from django.db.models import ForeignKey
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from dynamicforms import fields
from dynamicforms.action import Actions, FormButtonAction, FormButtonTypes, TableAction, TablePosition
from dynamicforms.mixins import DisplayMode, F
from dynamicforms.mixins.conditional_visibility import Operators, Statement
from dynamicforms.serializers import ModelSerializer, Serializer
from dynamicforms.template_render.layout import Column, Layout, Row
from dynamicforms.template_render.responsive_table_layout import ResponsiveTableLayout, ResponsiveTableLayouts
from dynamicforms.viewsets import ModelViewSet, SingleRecordViewSet
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.fields import empty
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from django_project_base.account.middleware import ProjectNotSelectedError
from django_project_base.licensing.logic import LicenseReportSerializer, LogAccessService
from django_project_base.notifications.base.channels.sms_channel import SmsChannel
from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.base.notification import Notification
from django_project_base.notifications.models import (
    DjangoProjectBaseNotification,
    SearchItems,
)
from django_project_base.utils import get_pk_name


class MessageBodyField(fields.RTFField):
    def __init__(self, *args, **kw):
        kw["write_only"] = True
        kw["label"] = _("Body")
        kw["display_table"] = DisplayMode.SUPPRESS
        super().__init__(*args, **kw)
        # TODO: if field is write only and not present in model serializer table, field is not rendered
        self.render_params["form_component_name"] = "DCKEditor"


class OrginalRecipientsField(fields.CharField):
    def to_representation(self, value, row_data=None):
        if row_data and row_data.recipients_original_payload_search:
            if len(row_data.recipients_original_payload_search) > 95:
                return f"{row_data.recipients_original_payload_search[:95]} ..."
            return row_data.recipients_original_payload_search
        if value:
            search_str = ",".join(
                list(
                    map(
                        str,
                        MessageToListField().parse(val=json.loads(value), return_instances=True),
                    )
                )
            )
            instance = self.parent.instance if self.parent else None
            if (
                instance
                and isinstance(instance, DjangoProjectBaseNotification)
                and not instance.recipients_original_payload_search
            ):
                instance.recipients_original_payload_search = search_str
                instance.save(update_fields=["recipients_original_payload_search"])
            # TODO: THIS SOLUTION FOR SEARCH IS BAD; BAD; -> MAKE BETTER ONE
            if isinstance(row_data, DjangoProjectBaseNotification) and not row_data.recipients_original_payload_search:
                row_data.recipients_original_payload_search = search_str
                row_data.save(update_fields=["recipients_original_payload_search"])
            if len(search_str) > 95:
                # TODO: INITIAL ROWS IN TABLE RENDER AND NOT HANDLED BY RENDER TO TABLE
                search_str = f"{search_str[:95]} ..."
            return search_str
        return super().to_representation(value, row_data)

    def render_to_table(self, value, row_data):
        val = super().render_to_table(value=value, row_data=row_data)
        if len(val) > 95:
            val = f"{val[:95]} ..."
        return val


class ReadOnlyDateTimeFieldFromTs(fields.DateTimeField):
    def to_representation(self, value, row_data=None):
        if value:
            return datetime.datetime.fromtimestamp(value).astimezone(pytz.utc)
        return value


class NotificationSerializer(ModelSerializer):
    template_context = dict(url_reverse="notification")
    form_titles = {"table": _("Messages"), "edit": _("New message")}
    boolean_render_params = fields.BooleanField().render_params

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        if self.is_filter:
            self.fields["delayed_to_display"].render_params = self.boolean_render_params
        self.fields.fields["level"].display_form = DisplayMode.HIDDEN
        self.fields.fields["type"].display_form = DisplayMode.HIDDEN
        self.fields.fields["project_slug"].display = DisplayMode.HIDDEN
        self.fields.fields["message_to"].child_relation.queryset = SearchItems.objects.get_queryset(
            request=self.request
        )
        self.fields.fields["send_notification_sms_text"].display = DisplayMode.SUPPRESS

        viewset = self.context.get("view")
        if viewset and viewset.kwargs.get("pk") and viewset.kwargs["pk"] == "new":
            self.actions.actions.append(
                FormButtonAction(
                    btn_type=FormButtonTypes.SUBMIT,
                    label=_("Save / Send later"),
                    name="send-later",
                    serializer=self,
                )
            )
            self.fields.fields["message_to"].allow_null = True

    id = fields.UUIDField(display=DisplayMode.HIDDEN)

    subject = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN, label=_("Subject"))
    recipients = fields.CharField(display_form=DisplayMode.HIDDEN, display_table=DisplayMode.HIDDEN)

    recipients_original_payload = OrginalRecipientsField(
        display_form=DisplayMode.HIDDEN, label=_("Recipients"), read_only=True, render_params={"max_width": "20em"}
    )

    delivery = fields.SerializerMethodField(label=_("Delivery"), display_form=DisplayMode.HIDDEN)

    level = fields.CharField(display=DisplayMode.SUPPRESS)
    type = fields.CharField(display=DisplayMode.SUPPRESS)

    message = fields.PrimaryKeyRelatedField(
        display_form=DisplayMode.SUPPRESS,
        display_table=DisplayMode.SUPPRESS,
        read_only=True,
    )

    actions = Actions(
        TableAction(
            TablePosition.HEADER,
            label=_("Add"),
            title=_("Add new notification"),
            name="add-notification",
            icon="ion-add-circle-outline",
        ),
        TableAction(
            TablePosition.HEADER,
            label=_("View license"),
            title=_("View license"),
            name="view-license",
            icon="ion-card-outline",
        ),
        TableAction(TablePosition.ROW_CLICK, _("Edit"), title=_("Edit record"), name="edit", icon="ion-pencil-outline"),
        FormButtonAction(
            btn_type=FormButtonTypes.CANCEL,
            name="cancel",
        ),
        FormButtonAction(
            btn_type=FormButtonTypes.SUBMIT,
            label=_("Send"),
            name="submit",
        ),
        add_form_buttons=False,
    )

    message_to = fields.ManyRelatedField(
        child_relation=fields.PrimaryKeyRelatedField(
            queryset=SearchItems.objects.get_queryset(),
            required=True,
        ),
        required=True,
        allow_null=False,
        write_only=True,
        display_table=DisplayMode.SUPPRESS,
        label=_("Recipients"),
    )

    message_subject = fields.CharField(write_only=True, label=_("Subject"), display_table=DisplayMode.HIDDEN)
    message_body = MessageBodyField()

    send_on_channels = fields.MultipleChoiceField(
        label=_("Send on channels"),
        allow_empty=False,
        display_table=DisplayMode.SUPPRESS,
        display_form=DisplayMode.FULL,
        choices=[(c.name, c.name) for c in ChannelIdentifier.supported_channels()],
        write_only=True,
    )

    send_notification_sms = fields.BooleanField(
        conditional_visibility=Statement(
            F("send_on_channels").not_includes(lambda: (SmsChannel.name)),
            Operators.AND,
            F("send_on_channels").includes(
                lambda: (
                    list(filter(lambda c: c.name != SmsChannel.name, ChannelIdentifier.supported_channels()))[0].name
                ),
            ),
        ),
        label=_("Send notification SMS"),
        display_table=DisplayMode.HIDDEN,
    )

    created_at = ReadOnlyDateTimeFieldFromTs(
        label=_("Created"),
        display_form=DisplayMode.HIDDEN,
        read_only=True,
        allow_null=True,
    )

    sent_at = ReadOnlyDateTimeFieldFromTs(
        label=_("Sent"),
        display_form=DisplayMode.HIDDEN,
        read_only=True,
        allow_null=True,
    )

    delayed_to_display = fields.SerializerMethodField(label=_("Delayed to"), display_form=DisplayMode.HIDDEN)

    # noinspection PyMethodMayBeStatic
    def get_delayed_to_display(self, rec: DjangoProjectBaseNotification):
        if rec.is_delayed:
            if rec.delayed_to == DjangoProjectBaseNotification.DELAYED_INDEFINITELY:
                return _("Indefinitely / Saved only")
            else:
                utc_time = datetime.datetime.fromtimestamp(rec.delayed_to)
                return utc_time.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_delivery(self, rec: DjangoProjectBaseNotification):
        req_channels = rec.required_channels.split(",") if rec.required_channels else []
        sent_channels = set(rec.sent_channels.split(",")) if rec.sent_channels else set()
        failed_channels = set(rec.failed_channels.split(",")) if rec.failed_channels else set()
        res = []
        for channel in req_channels:
            if channel in sent_channels:
                res.append(f'{channel} <span style="color: green">\u2714</span>')
            elif channel in failed_channels:
                title_attr = f"title=\"{rec.exceptions if rec.exceptions else ''}\""
                res.append(f'{channel} <span style="color: red" {title_attr}>\u2717</span>')
            else:
                res.append(f"{channel}")
        return ",".join(res)

    def to_representation(self, instance, row_data=None):
        repr = super().to_representation(instance, row_data)
        kw = getattr(self.context.get("view", object()), "kwargs", dict())
        if kw.get("pk") == "new" and kw.get("format") == "componentdef":
            # enable conditional field render in DF
            repr["send_on_channels"] = []
            repr["id"] = None
        return repr

    def get_subject(self, obj):
        if not obj or not obj.message:
            return None
        return obj.message.subject

    class Meta:
        model = DjangoProjectBaseNotification
        exclude = (
            "content_entity_context",
            "locale",
            "delayed_to",
            "recipients_original_payload_search",
            "exceptions",
            "extra_data",
            "counter",
            "required_channels",
            "sent_channels",
            "failed_channels",
            "done",
        )
        layout = Layout(
            Row(Column("message_to")),
            Row(Column("message_subject")),
            Row(Column("message_body")),
            Row(Column("send_on_channels")),
            size="large",
        )
        responsive_columns = ResponsiveTableLayouts(
            auto_generate_single_row_layout=True,
            auto_generate_single_column_layout=False,
            layouts=[
                ResponsiveTableLayout(
                    "subject",
                    "recipients_original_payload",
                    "created_at",
                    "sent_at",
                    "delayed_to_display",
                    auto_add_non_listed_columns=False,
                ),
                ResponsiveTableLayout(
                    [["subject", "created_at"], ["recipients_original_payload", "sent_at"], "delayed_to_display"],
                    auto_add_non_listed_columns=False,
                ),
                ResponsiveTableLayout(
                    "subject", "created_at", "sent_at", "delayed_to_display", auto_add_non_listed_columns=False
                ),
                ResponsiveTableLayout(
                    ["subject", "created_at", "sent_at", "delayed_to_display"], auto_add_non_listed_columns=False
                ),
            ],
        )


class MessageToListField(fields.ListField):
    def __init__(self, **kw):
        self.project_only_recipients = kw.pop("project_only_recipients", False)
        super().__init__(
            child=fields.CharField(),
            display_table=DisplayMode.SUPPRESS,
            **kw,
        )

    @staticmethod
    def parse(val: list, return_instances=False):
        users = list(filter(lambda i: i and "-" not in i and i.isnumeric(), map(str, val)))
        other_objects = list(filter(lambda i: i and "-" in i, map(str, val)))  # string 'RECORDID-CONTENTTYPEID'
        user_model = get_user_model()
        profile_model = swapper.load_model("django_project_base", "Profile")
        instances = []
        if return_instances:
            instances = list(
                filter(
                    lambda f: f,
                    [user_model.objects.filter(pk=u).first() for u in users],
                )
            )
        for obj in other_objects:
            _data = obj.split("-")
            instance = ContentType.objects.get(pk=_data[1]).model_class().objects.filter(pk=_data[0]).first()
            if not instance:
                continue
            if return_instances:
                instances += [instance]
                continue
            if isinstance(instance, (user_model, profile_model)):
                users += [instance.pk]
                continue
            if items_manager := next(filter(lambda i: "taggeditemthrough" in i, dir(instance)), None):
                for item in getattr(instance, items_manager).all():
                    if cont_object := getattr(item, "content_object", None):
                        if isinstance(cont_object, (user_model, profile_model)):
                            users += [cont_object.userprofile.pk]
                        elif user_related_fields := [
                            f
                            for f in cont_object._meta.fields
                            if isinstance(f, ForeignKey) and f.model in (profile_model, user_model)
                        ]:
                            for field in user_related_fields:
                                users += field.model.objects.filter(**{field.attname: cont_object.pk}).values_list(
                                    get_pk_name(field.model), flat=True
                                )
                        elif related_objects := [
                            item
                            for sub_list in [
                                # Jure: it doesn't matter that it's ContentType, as long as it's an empty queryset
                                [o for o in getattr(cont_object, i.name, ContentType.objects.none()).all()]
                                for i in cont_object._meta.related_objects
                            ]
                            for item in sub_list
                        ]:
                            users += list(
                                map(
                                    lambda g: g.pk,
                                    [
                                        getattr(obj, f.name, object)
                                        for obj in related_objects
                                        for f in obj._meta.fields
                                        if isinstance(f, ForeignKey)
                                        and isinstance(getattr(obj, f.name, object()), (profile_model, user_model))
                                    ],
                                )
                            )
        if return_instances:
            return instances
        return list(set(map(str, users)))

    def get_value(self, dictionary):
        value = super().get_value(dictionary)
        if not value:
            return []
        if value == empty:
            return MessageToListField.parse([])
        if isinstance(value[0], list):
            value = [item for sublist in value for item in sublist]
        ret = MessageToListField.parse(value)
        if self.project_only_recipients:
            if (request := self.context.get("request")) and getattr(request, "selected_project_slug", None):
                ret = list(
                    swapper.load_model("django_project_base", "ProjectMember")
                    # only current project members are returned as recipients
                    .objects.filter(member_id__in=list(map(int, ret)), project__slug=request.selected_project_slug)
                    .values_list("member_id", flat=True)
                )

        return ret


class DateTimeInfoField(fields.CharField):
    def __init__(self, placeholder: str = "Not sent", *args, **kwargs):
        kwargs["read_only"] = True
        super().__init__(*args, **kwargs)
        self.placeholder = placeholder

    def to_representation(self, value, row_data=None):
        if value:
            # Assuming timestamp is in Django's default timezone (UTC)
            utc_time = datetime.datetime.utcfromtimestamp(value).replace(tzinfo=timezone.get_current_timezone())
            return utc_time.strftime("%Y-%m-%d %H:%M:%S")
        return self.placeholder


class MessageBodyReadField(fields.SerializerMethodField):
    def __init__(self, *args, **kwargs):
        kwargs["display_table"] = DisplayMode.SUPPRESS
        super().__init__(*args, **kwargs)
        self.render_params["form_component_name"] = "DCKEditor"


class RecipientsSerializer(ModelSerializer):
    template_context = dict(url_reverse="notification")

    form_titles = {"table": _("Recipients"), "new": "", "edit": ""}

    actions = Actions(
        add_form_buttons=False,
        add_default_crud=False,
        add_default_filter=False,
    )

    full_name = fields.SerializerMethodField()

    show_filter = False

    # TODO: this is duplicated from ProfileSerializer... DPB
    def get_full_name(self, obj):
        # we have made it so that str(UserProfile) returns full_name, but possibly decorated with status (Klubis)
        return str(obj)

    def __init__(self, method_name=None, *args, **kwargs):
        self.method_name = method_name
        super().__init__(*args, **kwargs)
        self.display_table = DisplayMode.SUPPRESS

    class Meta:
        model = swapper.load_model("django_project_base", "Profile")
        fields = ("id", "full_name", "email")


class NotificationDetailSerializer(ModelSerializer):
    template_context = dict(url_reverse="notification")
    form_titles = {"new": _("Message")}

    actions = Actions(
        FormButtonAction(btn_type=FormButtonTypes.CANCEL, name="cancel", label=_("Close")),
        add_default_crud=False,
        add_form_buttons=False,
    )

    recipients_raw = RecipientsSerializer(many=True)
    message_subject = fields.SerializerMethodField()
    message_body = MessageBodyReadField()
    created_at = DateTimeInfoField(label=_("Created At"))
    sent_at = DateTimeInfoField(label=_("Sent At"))
    delayed_to_display = fields.SerializerMethodField(label=_("Delayed to"), display=DisplayMode.HIDDEN)

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        if self.instance and isinstance(self.instance, DjangoProjectBaseNotification) and self.instance.is_delayed:
            self.actions.actions.insert(
                0, FormButtonAction(btn_type=FormButtonTypes.CUSTOM, name="send", label=_("Send now"), serializer=self)
            )
            self.actions.actions.insert(
                1,
                FormButtonAction(
                    btn_type=FormButtonTypes.CUSTOM, name="send-later", label=_("Change delay"), serializer=self
                ),
            )
            self.fields["delayed_to_display"].display_form = DisplayMode.FULL

    # noinspection PyMethodMayBeStatic
    def get_message_to(self, obj: DjangoProjectBaseNotification):
        ids = [int(x) for x in obj.recipients.split(",")] if obj.recipients else []
        return swapper.load_model("django_project_base", "Profile").objects.filter(id__in=ids)

    # noinspection PyMethodMayBeStatic
    def get_message_subject(self, obj: DjangoProjectBaseNotification):
        return obj.message.subject if obj.message else ""

    # noinspection PyMethodMayBeStatic
    def get_message_body(self, obj: DjangoProjectBaseNotification):
        return obj.message.body if obj.message else ""

    # noinspection PyMethodMayBeStatic
    def get_delayed_to_display(self, obj: DjangoProjectBaseNotification):
        if obj.is_delayed:
            if obj.delayed_to == DjangoProjectBaseNotification.DELAYED_INDEFINITELY:
                return _("Indefinitely / Saved only")
            else:
                utc_time = datetime.datetime.fromtimestamp(obj.delayed_to)
                return utc_time.strftime("%Y-%m-%d %H:%M:%S")
        return None

    class Meta:
        model = DjangoProjectBaseNotification
        fields = (
            "recipients_raw",
            "message_subject",
            "message_body",
            "sent_at",
            "created_at",
            "id",
            "delayed_to_display",
        )
        layout = Layout(
            Row(Column("message_subject")),
            Row("created_at", "sent_at"),
            Row("delayed_to_display"),
            Row(Column("message_body")),
            Row(Column("recipients_raw")),
            size="large",
        )


class NotificationViewset(ModelViewSet):
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication,
    ]
    permission_classes = [IsAuthenticated]
    pagination_class = ModelViewSet.generate_paged_loader(ordering=["-created_at"])
    project_only_recipients = False

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.save_only = False

    def get_permissions(self):
        if self.action in ("notification_login", "notification_view"):
            return []
        else:
            return super().get_permissions()

    @extend_schema(exclude=True)
    @action(
        detail=True,
        methods=["GET"],
        url_name="notification-login",
        url_path="info",
        authentication_classes=[],
    )
    def notification_login(self, request, pk=None) -> HttpResponse:
        if not pk:
            raise PermissionDenied
        return render(
            request,
            "notification_login.html",
            dict(
                identifier=pk,
                url=reverse("notification-notification-view"),
                title=swapper.load_model("django_project_base", "Project")
                .objects.get(slug=DjangoProjectBaseNotification.objects.get(pk=pk).project_slug)
                .name,
            ),
        )

    @extend_schema(exclude=True)
    @action(
        methods=["POST"],
        detail=False,
        url_name="notification-view",
        authentication_classes=[],
        url_path="info-view",
    )
    def notification_view(self, request: Request, *args, **kwargs) -> HttpResponse:
        number: Optional[str] = request.data.get("number")
        identifier: Optional[str] = request.data.get("identifier")
        guest_accesses: List[float] = cache.get(identifier, [])
        now: float = time.time()
        if len(list(filter(lambda t: now - t < 60, guest_accesses))) > 4:
            # basic throttling
            raise PermissionDenied()
        guest_accesses.append(now)
        cache.set(identifier, guest_accesses, timeout=120)
        if not number or not identifier or len(number) < 4:
            raise ValidationError()
        notification: DjangoProjectBaseNotification = DjangoProjectBaseNotification.objects.filter(
            pk=identifier
        ).first()
        if not notification:
            raise Http404()

        phone_number_check = (
            get_user_model()
            .objects.filter(pk__in=notification.recipients.split(","))
            .filter(userprofile__phone_number__endswith=number)
            .exists()
        )
        if not phone_number_check:
            raise ValidationError()
        return render(
            request,
            "notification.html",
            dict(
                message_subject=notification.message.subject,
                message_body=notification.message.body,
                attachments=[(att.file.name, att.file.url) for att in notification.message.get_attachments()],
            ),
        )

    def filter_queryset_field(self, queryset, field, value):
        if field in ("created_at", "sent_at") and value and not value.isnumeric():
            # TODO: search by user defined time range
            try:
                # This one works in Klubis (Vue3... I left the one in exception, because it might work for some other case)
                value = int(datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp())
            except:
                value = int(datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
            return queryset.filter(**{f"{field}__gte": value - 1800, f"{field}__lte": value + 1800})

        if field == "recipients_original_payload" and value:
            return queryset.filter(**{"recipients_original_payload_search__icontains": value})
        if field == "subject" and value:
            return queryset.filter(**{"message__subject__icontains": value})
        if field == "delivery" and value:
            return queryset.filter(**{"required_channels__icontains": value})
        if field == "delayed_to_display":
            if value == "true":
                return queryset.filter(delayed_to__gte=int(datetime.datetime.now().timestamp()))
            elif value == "false":
                return queryset.exclude(delayed_to__gte=int(datetime.datetime.now().timestamp()))

        return super().filter_queryset_field(queryset, field, value)

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            try:
                instance = self.get_object()
            except:
                instance = None
            if not instance or instance._state.adding:

                class NewMessageSerializer(Serializer):
                    form_titles = {"edit": _("New message")}

                    message_body = NotificationSerializer().fields.fields["message_body"]
                    message_subject = NotificationSerializer().fields.fields["message_subject"]
                    message_to = MessageToListField(
                        allow_null=False, allow_empty=False, project_only_recipients=self.project_only_recipients
                    )
                    send_on_channels = fields.ListField(
                        label=_("Send on channels"),
                        child=fields.CharField(),
                        allow_empty=False,
                        required=True,
                        display_table=DisplayMode.SUPPRESS,
                        display_form=DisplayMode.SUPPRESS,
                    )
                    send_notification_sms = fields.BooleanField(default=False, allow_null=False)
                    delayed_to = fields.DateTimeField(label=_("Delayed to"), display=DisplayMode.HIDDEN, required=False)

                return NewMessageSerializer
        if self.action == "retrieve" and self.kwargs["pk"] and self.kwargs["pk"] != "new":
            return NotificationDetailSerializer
        return NotificationSerializer

    def get_queryset(self):
        try:
            return DjangoProjectBaseNotification.objects.filter(
                project_slug=self.request.selected_project_slug
            ).order_by("-created_at")
        except ProjectNotSelectedError as e:
            raise NotFound(e.message)

    def _create_notification(self, serializer):
        Notification.create_notification(
            self.request,
            serializer.validated_data["message_subject"],
            serializer.validated_data["message_body"],
            serializer.validated_data["message_to"],
            serializer.validated_data["send_on_channels"],
            serializer.validated_data["send_notification_sms"],
            raw_recipients=self.request.data["message_to"],
            save_only=self.save_only,
            delayed_to=serializer.validated_data.get("delayed_to"),
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        if request.data.pop("send", None):
            from django_project_base.notifications.base.queable_notification_mixin import QueableNotificationMixin

            notification = self.get_object()
            notification.delayed_to = int(datetime.datetime.now().timestamp())
            notification.save(update_fields=["delayed_to"])
            notification.prepare_for_send(request.user.pk)

            QueableNotificationMixin().enqueue_notification(notification, notification.extra_data)
            serializer = self.get_serializer(notification)
            return Response(serializer.data)
        if request.data.pop("send_later", False):
            save_only = request.data.pop("save_only", False)
            if save_only:
                delayed_to = DjangoProjectBaseNotification.DELAYED_INDEFINITELY
            else:
                try:
                    delayed_to = datetime.datetime.fromisoformat(request.data.pop("delayed_to", None)).timestamp()
                except:
                    raise ValidationError(_("Invalid delayed to value"))

            notification = self.get_object()
            notification.delayed_to = int(delayed_to)
            notification.save(update_fields=["delayed_to"])
            serializer = self.get_serializer(notification)
            return Response(serializer.data)

        kwargs.pop("pk", None)
        self.kwargs["pk"] = "new"
        self.save_only = request.data.pop("save_only", False)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        kwargs.pop("pk", None)
        if request.data.pop("send_later", False):
            self.save_only = request.data.pop("save_only", False)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        return self._create_notification(serializer)


class NotificationsLicenseSerializer(LicenseReportSerializer):
    template_context = dict(url_reverse="notification-license")

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        if (request := self.context.get("request")) and not fields.BooleanField().to_internal_value(
            request.query_params.get("decorate-max-price", "0")
        ):
            self.fields.pop("max_notification_price", None)
        for channel in ChannelIdentifier.supported_channels():
            self.fields[channel.name] = fields.IntegerField(read_only=True, label=_(channel.verbose_name))

    usage_report = None
    max_notification_price = fields.FloatField(read_only=True, display_table=DisplayMode.HIDDEN)
    actions = Actions(
        FormButtonAction(btn_type=FormButtonTypes.CANCEL, name="cancel"),
        add_default_crud=False,
        add_default_filter=False,
        add_form_buttons=False,
    )

    class Meta:
        layout = Layout(Row("credit", "used_credit", "remaining_credit"), Row("EMail", "SMS"))


class NotificationsLicenseViewSet(SingleRecordViewSet):
    serializer_class = NotificationsLicenseSerializer

    permission_classes = (IsAuthenticated,)

    def new_object(self):
        license = LogAccessService().report(user=self.request.user)
        usage = 0
        if notifications_usage := next(
            filter(
                lambda u: u.get("item", "") == DjangoProjectBaseNotification._meta.verbose_name,
                license["usage_report"],
            ),
            None,
        ):
            usage = notifications_usage["usage_sum"]
        license["used_credit"] = usage

        license["channels"] = {}
        max_price = 0
        for channel in ChannelIdentifier.supported_channels():
            price = channel.notification_price
            if price > max_price:
                max_price = price
            license[channel.name] = int(max([license["remaining_credit"] / price, 0]))
        if fields.BooleanField().to_internal_value(self.request.query_params.get("decorate-max-price", "0")):
            license["max_notification_price"] = max_price

        return NotificationsLicenseSerializer(license).data

    def create(self, request, *args, **kwargs) -> Response:
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class NotificationDelaySerializer(Serializer):
    template_context = dict(url_reverse="notification-delay")

    form_titles = {
        "table": "",
        "new": _("Delayed sending"),
        "edit": "",
    }

    actions = Actions(
        FormButtonAction(btn_type=FormButtonTypes.CANCEL, name="cancel", label=_("Back")),
        FormButtonAction(btn_type=FormButtonTypes.SUBMIT, name="submit", label=_("Confirm")),
        add_default_crud=False,
        add_form_buttons=False,
    )
    delayed_to = fields.DateTimeField(
        label=_("Send at"),
        conditional_visibility=F("save_only") != True,  # noqa: E712  # To mora biti tako... drugače preverjanje ne dela pravilno
    )

    save_only = fields.BooleanField(label=_("Delay indefinitely / Save only"), default=True)

    class Meta:
        layout = Layout(
            Row(Column("save_only")),
            Row(Column("delayed_to")),
            size="medium",
        )


class NotificationDelayViewSet(SingleRecordViewSet):
    serializer_class = NotificationDelaySerializer

    permission_classes = (IsAuthenticated,)

    def new_object(self):
        notification = self.request.query_params.get("notification_id", None)
        if notification and notification != "new":
            try:
                notification = (
                    DjangoProjectBaseNotification.objects.filter(id=notification).order_by("-created_at").first()
                )
            except:
                notification = None
        else:
            notification = None
        delayed_to = DjangoProjectBaseNotification.DELAYED_INDEFINITELY
        if notification:
            delayed_to = notification.delayed_to

        save_only = delayed_to == DjangoProjectBaseNotification.DELAYED_INDEFINITELY
        if save_only or not delayed_to:
            delayed_to = datetime.datetime.now()
        else:
            delayed_to = datetime.datetime.fromtimestamp(delayed_to)
        return dict(
            delayed_to=delayed_to,
            save_only=save_only,
        )
