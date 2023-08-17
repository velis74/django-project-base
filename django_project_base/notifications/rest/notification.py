import datetime

import swapper
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import ForeignKey
from django.utils.crypto import get_random_string
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
from django_project_base.notifications.base.notification import Notification
from django_project_base.notifications.models import (
    DjangoProjectBaseMessage,
    DjangoProjectBaseNotification,
    SearchItems,
)


class CommaSeparatedChannelField(fields.CharField):
    def render_to_table(self, value, row_data):
        return value


class CommaSeparatedRecipientsField(fields.CharField):
    def render_to_table(self, value, row_data):
        if value is None:
            return value
        return ",".join(
            [getattr(get_user_model().objects.filter(pk=u).first() or object(), "email", "") for u in value.split(",")]
        )


class MessageBodyField(fields.RTFField):
    def __init__(self, *args, **kw):
        kw["write_only"] = True
        kw["label"] = _("Body")
        kw["display_table"] = DisplayMode.HIDDEN
        super().__init__(*args, **kw)
        # TODO: if field is write only and not present in model serializer table, field is not rendered
        self.render_params["form_component_name"] = "DCKEditor"


class NotificationSerializer(ModelSerializer):
    template_context = dict(url_reverse="notification")

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        self.fields.fields["level"].display_form = DisplayMode.HIDDEN
        self.fields.fields["type"].display_form = DisplayMode.HIDDEN
        self.fields.fields["sent_at"].display_form = DisplayMode.HIDDEN

    id = fields.UUIDField(display=DisplayMode.HIDDEN)

    subject = fields.SerializerMethodField(display_form=DisplayMode.HIDDEN)
    recipients = CommaSeparatedRecipientsField(display_form=DisplayMode.HIDDEN)

    required_channels = CommaSeparatedChannelField(display_form=DisplayMode.HIDDEN)
    sent_channels = CommaSeparatedChannelField(display_form=DisplayMode.HIDDEN)
    failed_channels = CommaSeparatedChannelField(display_form=DisplayMode.HIDDEN)

    counter = fields.IntegerField(display_form=DisplayMode.HIDDEN)
    exceptions = fields.CharField(display_form=DisplayMode.HIDDEN)

    level = fields.CharField(display=DisplayMode.SUPPRESS)
    type = fields.CharField(display=DisplayMode.SUPPRESS)

    message = fields.PrimaryKeyRelatedField(
        display_form=DisplayMode.SUPPRESS, display_table=DisplayMode.SUPPRESS, read_only=True
    )

    actions = Actions(
        TableAction(TablePosition.HEADER, _("Add"), title=_("Add new record"), name="add", icon="add-circle-outline")
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

    def get_subject(self, obj):
        if not obj or not obj.message:
            return None
        return obj.message.subject

    class Meta:
        model = DjangoProjectBaseNotification
        exclude = ("content_entity_context", "locale", "created_at", "delayed_to")
        layout = Layout(
            Row(
                Column("message_subject"),
            ),
            Row(Column("message_body")),
            Row(Column("message_to")),
            Row(Column("send_on_channels")),
            size="large",
        )
        responsive_columns = ResponsiveTableLayouts(
            layouts=[
                ResponsiveTableLayout(),
                ResponsiveTableLayout(
                    "recipients",
                    "subject",
                    "required_channels",
                    "sent_channels",
                    "failed_channels",
                    "exceptions",
                    "counter",
                    "sent_at",
                    auto_add_non_listed_columns=False,
                ),
            ]
        )


class MessageToListField(fields.ListField):
    def __init__(self, **kw):
        super().__init__(child=fields.CharField(), required=True, display_table=DisplayMode.SUPPRESS, **kw)

    def get_value(self, dictionary):
        value = super().get_value(dictionary)
        if not value:
            return []
        users = list(filter(lambda i: i and "-" not in i, value))
        other_objects = list(filter(lambda i: i and "-" in i, value))  # string 'RECORDID-CONTENTTYPEID'
        user_model = get_user_model()
        profile_model = swapper.load_model("django_project_base", "Profile")
        for obj in other_objects:
            _data = obj.split("-")
            instance = ContentType.objects.get(pk=_data[1]).model_class().objects.get(pk=_data[0])
            if isinstance(instance, (user_model, profile_model)):
                users += [instance.pk]
                continue
            if items_manager := next(filter(lambda i: "taggeditemthrough" in i, dir(instance)), None):
                for item in getattr(instance, items_manager).all():
                    if cont_object := getattr(item, "content_object", None):
                        if isinstance(
                            cont_object, (get_user_model(), swapper.load_model("django_project_base", "Profile"))
                        ):
                            users += [cont_object.userprofile.pk]
                        elif user_related_fields := [
                            f
                            for f in cont_object._meta.fields
                            if isinstance(f, ForeignKey) and f.model in (profile_model, user_model)
                        ]:
                            for field in user_related_fields:
                                users += field.model.objects.filter(**{field.attname: cont_object.pk}).values_list(
                                    field.model._meta.pk.name, flat=True
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
                                        getattr(related_objects[0], f.name, object)
                                        for f in related_objects[0]._meta.fields
                                        if isinstance(f, ForeignKey)
                                        and isinstance(  # noqa: W503
                                            getattr(related_objects[0], f.name, object()), (profile_model, user_model)
                                        )
                                    ],
                                )
                            )
        return list(set(map(str, users)))


class NotificationViewset(ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if not self.detail and self.action == "create":

            class NewMessageSerializer(Serializer):
                message_body = NotificationSerializer().fields.fields["message_body"]
                message_subject = NotificationSerializer().fields.fields["message_subject"]
                message_to = MessageToListField()
                send_on_channels = fields.ListField(
                    child=fields.CharField(required=True),
                    required=True,
                    display_table=DisplayMode.SUPPRESS,
                    display_form=DisplayMode.SUPPRESS,
                )

            return NewMessageSerializer
        return NotificationSerializer

    def get_queryset(self):
        return DjangoProjectBaseNotification.objects.filter(
            project__slug=getattr(
                self.request,
                settings.DJANGO_PROJECT_BASE_BASE_REQUEST_URL_VARIABLES["project"]["value_name"],
                get_random_string(length=32).decode(),
            )
        ).order_by("-sent_at")

    def perform_create(self, serializer):
        notification = Notification(
            message=DjangoProjectBaseMessage(
                subject=serializer.validated_data["message_subject"],
                body=serializer.validated_data["message_body"],
                footer="",
                content_type=DjangoProjectBaseMessage.PLAIN_TEXT,
            ),
            recipients=serializer.validated_data["message_to"],
            delay=int(datetime.datetime.now().timestamp()),
            channels=[ChannelIdentifier.channel(c).__class__ for c in serializer.validated_data["send_on_channels"]],
            persist=True,
        )
        notification.send()
