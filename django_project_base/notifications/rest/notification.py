import datetime

from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _
from dynamicforms import fields
from dynamicforms.action import Actions
from dynamicforms.mixins import DisplayMode
from dynamicforms.serializers import ModelSerializer
from dynamicforms.template_render.layout import Column, Layout, Row
from dynamicforms.template_render.responsive_table_layout import ResponsiveTableLayout, ResponsiveTableLayouts
from dynamicforms.viewsets import ModelViewSet
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django_project_base.notifications.base.enums import ChannelIdentifier
from django_project_base.notifications.models import DjangoProjectBaseNotification


class NotificationSerializer(ModelSerializer):
    template_context = dict(url_reverse="notification")

    subject = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)
    recipients = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)

    required_channels = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)
    sent_channels = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)
    failed_channels = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)
    sent_at = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)

    counter = fields.IntegerField(display_form=DisplayMode.HIDDEN)
    exceptions = fields.CharField(display_form=DisplayMode.HIDDEN)

    message = fields.PrimaryKeyRelatedField(display_form=DisplayMode.HIDDEN, read_only=True)
    level = fields.CharField(display_form=DisplayMode.HIDDEN)
    type = fields.CharField(display_form=DisplayMode.HIDDEN)

    actions = Actions(add_default_crud=True)

    users_write = fields.ManyRelatedField(
        child_relation=fields.PrimaryKeyRelatedField(
            help_text=_("aaaa bbbbb."),
            queryset=get_user_model().objects.all(),
            required=True,
        ),
        help_text=_("aaaaaaaa."),
        required=True,
        allow_null=False,
        write_only=True,
        display_table=DisplayMode.HIDDEN,
    )
    subject_write = fields.CharField(write_only=True, label=_("SubjectX"), display_table=DisplayMode.HIDDEN)
    body_write = fields.CharField(write_only=True, label=_("BodyX"), display_table=DisplayMode.HIDDEN)

    def get_sent_at(self, obj):
        if not obj or not obj.sent_at:
            return None
        return make_aware(datetime.datetime.fromtimestamp(obj.sent_at))

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
        return NotificationSerializer

    def get_queryset(self):
        return DjangoProjectBaseNotification.objects.all()
