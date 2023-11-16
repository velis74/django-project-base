import datetime
import json
import time
from typing import List, Optional

import pytz
import swapper
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import ForeignKey, QuerySet
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
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
    DjangoProjectBaseMessage,
    DjangoProjectBaseNotification,
    SearchItems,
)
from django_project_base.utils import get_host_url, get_pk_name


class MessageBodyField(fields.RTFField):
    def __init__(self, *args, **kw):
        kw["write_only"] = True
        kw["label"] = _("Body")
        kw["display_table"] = DisplayMode.HIDDEN
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
            if (
                self.parent
                and self.parent.instance  # noqa: W503
                and not isinstance(self.parent.instance, QuerySet)  # noqa: W503
                and not self.parent.instance.recipients_original_payload_search  # noqa: W503
            ):
                self.parent.instance.recipients_original_payload_search = search_str
                self.parent.instance.save(update_fields=["recipients_original_payload_search"])
            # TODO: THIS SOLUTION FOR SEARCH IS BAD; BAD; -> MAKE BETTER ONE
            if row_data and not row_data.recipients_original_payload_search:
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

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        self.fields.fields["level"].display_form = DisplayMode.HIDDEN
        self.fields.fields["type"].display_form = DisplayMode.HIDDEN
        self.fields.fields["project_slug"].display = DisplayMode.HIDDEN
        self.fields.fields["message_to"].child_relation.queryset = SearchItems.objects.get_queryset(
            request=self.request
        )
        self.fields.fields["send_notification_sms_text"].display = DisplayMode.SUPPRESS

    id = fields.UUIDField(display=DisplayMode.HIDDEN)

    subject = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)
    recipients = fields.CharField(display_form=DisplayMode.HIDDEN, display_table=DisplayMode.HIDDEN)

    recipients_original_payload = OrginalRecipientsField(
        display_form=DisplayMode.HIDDEN, label=_("Recipients"), read_only=True
    )

    required_channels = fields.CharField(display_form=DisplayMode.HIDDEN)
    sent_channels = fields.CharField(display_form=DisplayMode.HIDDEN)
    failed_channels = fields.CharField(display_form=DisplayMode.HIDDEN)

    counter = fields.IntegerField(display_form=DisplayMode.HIDDEN)

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
            _("Add"),
            title=_("Add new record"),
            name="add-notification",
            icon="add-circle-outline",
        ),
        TableAction(
            TablePosition.HEADER,
            _("View license"),
            title=_("View license"),
            name="view-license",
            icon="card-outline",
        ),
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

    sent_at = ReadOnlyDateTimeFieldFromTs(display_form=DisplayMode.HIDDEN, read_only=True, allow_null=True)

    def to_representation(self, instance, row_data=None):
        repr = super().to_representation(instance, row_data)
        kw = getattr(self.context.get("view", object()), "kwargs", dict())
        if kw.get("pk") == "new" and kw.get("format") == "componentdef":
            # enable conditional field render in DF
            repr["send_on_channels"] = []
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
            "created_at",
            "delayed_to",
            "recipients_original_payload_search",
            "exceptions",
        )
        layout = Layout(
            Row(Column("message_to")),
            Row(
                Column("message_subject"),
            ),
            Row(Column("message_body")),
            Row(Column("send_on_channels")),
            size="large",
        )
        responsive_columns = ResponsiveTableLayouts(
            layouts=[
                ResponsiveTableLayout(),
                ResponsiveTableLayout(
                    "recipients_original_payload",
                    "subject",
                    "required_channels",
                    "sent_channels",
                    "failed_channels",
                    "counter",
                    "sent_at",
                    auto_add_non_listed_columns=False,
                ),
            ]
        )


class MessageToListField(fields.ListField):
    def __init__(self, **kw):
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
                                [o for o in getattr(cont_object, i.name, []).all()]
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
        return MessageToListField.parse(value)


class NotificationViewset(ModelViewSet):
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication,
    ]
    permission_classes = [IsAuthenticated]

    @extend_schema(exclude=True)
    @action(
        detail=True,
        methods=["GET"],
        url_name="notification-login",
        url_path="info",
        permission_classes=[],
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
        permission_classes=[],
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
            dict(message=notification.message.subject + "</br></br></br>" + notification.message.body),
        )

    def filter_queryset_field(self, queryset, field, value):
        if field == "sent_at" and value and not value.isnumeric():
            # TODO: search by user defined time range
            value = int(datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())
            return queryset.filter(**{f"{field}__gte": value - 1800, f"{field}__lte": value + 1800})

        if field == "recipients_original_payload" and value:
            return queryset.filter(**{"recipients_original_payload_search__icontains": value})
        return super().filter_queryset_field(queryset, field, value)

    def get_serializer_class(self):
        if self.action in ("create", "update"):

            class NewMessageSerializer(Serializer):
                message_body = NotificationSerializer().fields.fields["message_body"]
                message_subject = NotificationSerializer().fields.fields["message_subject"]
                message_to = MessageToListField(allow_null=False, allow_empty=False)
                send_on_channels = fields.ListField(
                    child=fields.CharField(),
                    required=True,
                    display_table=DisplayMode.SUPPRESS,
                    display_form=DisplayMode.SUPPRESS,
                )
                send_notification_sms = fields.BooleanField(default=False, allow_null=False)

            return NewMessageSerializer
        return NotificationSerializer

    def get_queryset(self):
        try:
            return DjangoProjectBaseNotification.objects.filter(
                project_slug=self.request.selected_project_slug
            ).order_by("-sent_at")
        except ProjectNotSelectedError as e:
            raise NotFound(e.message)

    def _create_notification(self, serializer):
        host_url = get_host_url(self.request)
        notification = Notification(
            message=DjangoProjectBaseMessage(
                subject=serializer.validated_data["message_subject"],
                body=serializer.validated_data["message_body"],
                footer="",
                content_type=DjangoProjectBaseMessage.HTML,
            ),
            raw_recipents=self.request.data["message_to"],
            project=swapper.load_model("django_project_base", "Project")
            .objects.get(slug=self.request.selected_project_slug)
            .slug,
            recipients=serializer.validated_data["message_to"],
            delay=int(datetime.datetime.now().timestamp()),
            channels=[
                ChannelIdentifier.channel(c, extra_data=None, project_slug=None).__class__
                for c in serializer.validated_data["send_on_channels"]
            ],
            persist=True,
            user=self.request.user.pk,
            send_notification_sms=serializer.validated_data["send_notification_sms"],
            host_url=host_url,
        )
        notification.send()

    def update(self, request, *args, **kwargs):
        kwargs.pop("pk", None)
        return super().create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kwargs.pop("pk", None)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        return self._create_notification(serializer)


class ChannelSerializer(Serializer):
    available = fields.FloatField(read_only=True, display_table=DisplayMode.HIDDEN)


class ChannelsSerializer(Serializer):
    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        for channel in ChannelIdentifier.supported_channels():
            self.fields[channel.name] = ChannelSerializer()


class NotificationsLicenseSerializer(LicenseReportSerializer):
    template_context = dict(url_reverse="notification-license")

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        if (request := self.context.get("request")) and not fields.BooleanField().to_internal_value(
            request.query_params.get("decorate-max-price", "0")
        ):
            self.fields.pop("max_notification_price", None)

    usage_report = None
    channels = ChannelsSerializer()
    max_notification_price = fields.FloatField(read_only=True, display_table=DisplayMode.HIDDEN)
    actions = Actions(
        FormButtonAction(btn_type=FormButtonTypes.CANCEL, name="cancel"),
        add_default_crud=False,
        add_default_filter=False,
        add_form_buttons=False,
    )


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
            license["channels"][channel.name] = {}
            license["channels"][channel.name]["available"] = int(max([license["remaining_credit"] / price, 0]))
        if fields.BooleanField().to_internal_value(self.request.query_params.get("decorate-max-price", "0")):
            license["max_notification_price"] = max_price

        return NotificationsLicenseSerializer(license).data

    def create(self, request, *args, **kwargs) -> Response:
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
