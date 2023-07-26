import datetime

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from dynamicforms import fields
from dynamicforms.action import Actions, TableAction, TablePosition
from dynamicforms.mixins import DisplayMode
from dynamicforms.serializers import ModelSerializer, Serializer
from dynamicforms.template_render.layout import Column, Layout, Row
from dynamicforms.template_render.responsive_table_layout import ResponsiveTableLayout, ResponsiveTableLayouts
from dynamicforms.viewsets import ModelViewSet
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.email_notification import EMailNotification
from django_project_base.notifications.models import DjangoProjectBaseMessage, DjangoProjectBaseNotification


class NotificationSerializer(ModelSerializer):
    template_context = dict(url_reverse="notification")

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        self.fields.fields["level"].display_form = DisplayMode.HIDDEN
        self.fields.fields["type"].display_form = DisplayMode.HIDDEN
        self.fields.fields["sent_at"].display_form = DisplayMode.HIDDEN

    subject = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)
    recipients = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)

    required_channels = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)
    sent_channels = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)
    failed_channels = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)

    counter = fields.IntegerField(display_form=DisplayMode.HIDDEN)
    exceptions = fields.CharField(display_form=DisplayMode.HIDDEN)

    message = fields.PrimaryKeyRelatedField(display_form=DisplayMode.HIDDEN, read_only=True)

    actions = Actions(
        TableAction(TablePosition.HEADER, _("Add"), title=_("Add new record"), name="add", icon="add-circle-outline")
    )

    users_write = fields.ManyRelatedField(
        child_relation=fields.PrimaryKeyRelatedField(
            queryset=get_user_model().objects.all(),
            required=True,
        ),
        required=True,
        allow_null=False,
        write_only=True,
        display_table=DisplayMode.HIDDEN,
        label=_("Recipients"),
    )
    subject_write = fields.CharField(write_only=True, label=_("Subject"), display_table=DisplayMode.HIDDEN)
    body_write = fields.CharField(write_only=True, label=_("Body"), display_table=DisplayMode.HIDDEN)

    def get_subject(self, obj):
        if not obj or not obj.message:
            return None
        return obj.message.subject

    def get_recipients(self, obj):
        if not obj or not obj.recipients:
            return None
        return ",".join(
            [
                getattr(get_user_model().objects.filter(pk=u).first() or object(), "email", "")
                for u in obj.recipients.split(",")
            ]
        )

    def get_required_channels(self, obj):
        if not obj or not obj.required_channels:
            return None
        return ",".join([ChannelIdentifier.channel(int(c)).name for c in obj.required_channels.split(",")])

    def get_sent_channels(self, obj):
        if not obj or not obj.sent_channels:
            return None
        return ",".join([ChannelIdentifier.channel(int(c)).name for c in obj.sent_channels.split(",")])

    def get_failed_channels(self, obj):
        if not obj or not obj.failed_channels:
            return None
        return ",".join([ChannelIdentifier.channel(int(c)).name for c in obj.failed_channels.split(",")])

    class Meta:
        model = DjangoProjectBaseNotification
        exclude = ("content_entity_context", "locale", "created_at", "delayed_to")
        layout = Layout(
            Row(Column("users_write")),
            Row(
                Column("subject_write"),
            ),
            Row(Column("body_write")),
            size="large",
        )
        responsive_columns = ResponsiveTableLayouts(
            auto_generate_single_row_layout=True,
            layouts=[
                ResponsiveTableLayout(auto_add_non_listed_columns=True),
                ResponsiveTableLayout(
                    "recipients",
                    "subject",
                    # "body",
                    "level",
                    "type",
                    "required_channels",
                    "sent_channels",
                    "failed_channels",
                    "exceptions",
                    "counter",
                    "sent_at",
                    auto_add_non_listed_columns=False,
                ),
            ],
        )


class NotificationViewset(ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if not self.detail and self.action == "create":

            class NewMessageSerializer(Serializer):
                body_write = NotificationSerializer().fields.fields["body_write"]
                subject_write = NotificationSerializer().fields.fields["subject_write"]
                users_write = NotificationSerializer().fields.fields["users_write"]

            return NewMessageSerializer
        return NotificationSerializer

    def get_queryset(self):
        return DjangoProjectBaseNotification.objects.all().order_by("-sent_at")

    def perform_create(self, serializer):
        EMailNotification(
            message=DjangoProjectBaseMessage(
                subject=serializer.validated_data["subject_write"],
                body=serializer.validated_data["body_write"],
                footer="",
                content_type=DjangoProjectBaseMessage.PLAIN_TEXT,
            ),
            recipients=[u.pk for u in serializer.validated_data["users_write"]],
            delay=int(datetime.datetime.now().timestamp()),
        ).send()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
