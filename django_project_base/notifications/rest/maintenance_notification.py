import datetime

from typing import Optional

from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from dynamicforms.serializers import ModelSerializer as DFSerializer
from dynamicforms.viewsets import ModelViewSet
from rest_framework import fields, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, Serializer as RestFrameworkSerializer

from django_project_base.notifications.base.enums import NotificationType
from django_project_base.notifications.maintenance_notification import MaintenanceNotification
from django_project_base.notifications.models import DjangoProjectBaseMessage, DjangoProjectBaseNotification
from django_project_base.notifications.utils import utc_now
from django_project_base.utils import get_pk_name


class NotificationAcknowledgedRequestSerializer(RestFrameworkSerializer):
    def __new__(cls, *args, **kwargs):
        new: "NotificationAcknowledgedRequestSerializer" = super().__new__(cls, *args, **kwargs)
        new.fields[get_pk_name(DjangoProjectBaseMessage)] = fields.UUIDField(
            required=True, allow_null=False, help_text="Notification identifier"
        )
        new.fields["acknowledged_identifier"] = fields.IntegerField(
            required=True,
            allow_null=False,
            help_text=_("Time interval identifying at what time notification was acknowledged by user"),
        )
        return new

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class MessageSerializer(DFSerializer):
    class Meta:
        model = DjangoProjectBaseMessage
        exclude = (get_pk_name(DjangoProjectBaseMessage),)


class MaintenanceNotificationSerializer(ModelSerializer):
    notification_acknowledged_data = fields.SerializerMethodField()
    message = MessageSerializer()

    def get_notification_acknowledged_data(self, notification: DjangoProjectBaseNotification) -> list:
        request: Optional[Request] = self.context.get("request")
        return request.session.get(settings.MAINTENANCE_NOTIFICATIONS_CACHE_KEY, {}).get(str(notification.pk), [])

    def create(self, validated_data) -> DjangoProjectBaseNotification:
        try:
            message: DjangoProjectBaseMessage = DjangoProjectBaseMessage.objects.create(**validated_data["message"])
            return MaintenanceNotification(delay=validated_data["delayed_to"], message=message).send()
        except AssertionError as ae:
            raise ValidationError(str(ae))
        except Exception as e:
            raise APIException(e)

    # todo: update and partial update, destroy

    def validate(self, attrs: dict):
        _type: Optional[str] = attrs.get("type")
        if _type and _type != NotificationType.MAINTENANCE.value:
            raise ValidationError({"type": "Only type %s allowed." % NotificationType.MAINTENANCE.value})
        time_delta: int = settings.TIME_BUFFER_FOR_CURRENT_MAINTENANCE_API_QUERY
        existing_maintenances: list = DjangoProjectBaseNotification.objects.filter(
            delayed_to__range=[attrs["delayed_to"] - time_delta, attrs["delayed_to"] + time_delta]
        )
        if bool(len(existing_maintenances)):
            raise ValidationError({"delayed_to": "Another maintenance is planned at this time"})
        return super().validate(attrs)

    class Meta:
        model = DjangoProjectBaseNotification
        exclude = (
            "required_channels",
            "sent_channels",
            "failed_channels",
            "recipients",
            "recipients_original_payload",
            "level",
            "sent_at",
            "type",
            "content_entity_context",
        )


@extend_schema_view(
    destroy=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
)
class UsersMaintenanceNotificationViewset(ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return MaintenanceNotificationSerializer

    def get_queryset(self):
        now: int = utc_now().timestamp()
        return DjangoProjectBaseNotification.objects.filter(
            type=NotificationType.MAINTENANCE.value,
            delayed_to__gt=now,
            delayed_to__lt=now + datetime.timedelta(hours=8).total_seconds(),
        )

    @extend_schema(request=MaintenanceNotificationSerializer(), description="Create maintenance notification.")
    @transaction.atomic
    def create(self, request: Request, *args, **kwargs) -> Response:
        return super().create(request, *args, **kwargs)

    @extend_schema(
        request=MaintenanceNotificationSerializer(many=True),
        description="List's maintenance notifications that are planned in future.",
        parameters=[
            OpenApiParameter(
                name="current",
                description="If present in request and if true, then this api "
                "returns only maintenance notification that is planned in range "
                "of now +/- TIME_BUFFER_FOR_CURRENT_MAINTENANCE_API_QUERY settings value.",
                required=False,
                type=bool,
            ),
        ],
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        if request.query_params.get("current", "False") in fields.BooleanField.TRUE_VALUES:
            now: float = utc_now().timestamp()
            time_delta: int = settings.TIME_BUFFER_FOR_CURRENT_MAINTENANCE_API_QUERY
            current_maintenance: Optional[DjangoProjectBaseNotification] = next(
                iter(
                    DjangoProjectBaseNotification.objects.filter(delayed_to__range=[now - time_delta, now + time_delta])
                ),
                None,
            )
            return Response(self.get_serializer(current_maintenance, many=False).data)
        read_notifications: dict = request.session.get(settings.MAINTENANCE_NOTIFICATIONS_CACHE_KEY, {})
        pk_name: str = get_pk_name(DjangoProjectBaseMessage)
        return Response(
            self.get_serializer(
                filter(lambda n: len(read_notifications.get(str(getattr(n, pk_name)), [])) < 3, self.get_queryset()),
                many=True,
            ).data
        )

    @extend_schema(description="Get single maintenance notification's data")
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        return super().retrieve(request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)
        return super().partial_update(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request: Request, *args, **kwargs) -> Response:
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request: Request, *args, **kwargs) -> Response:
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        request=NotificationAcknowledgedRequestSerializer(),
        description="Mark message as acknowledged by user making request.",
        responses={status.HTTP_201_CREATED: None},
    )
    @action(methods=["POST"], detail=False, url_path="acknowledged", url_name="acknowledged")
    def acknowledged(self, request: Request, **kwargs) -> Response:
        # todo: storage for acknowledged notifications should be configurable
        ser: NotificationAcknowledgedRequestSerializer = NotificationAcknowledgedRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        if settings.MAINTENANCE_NOTIFICATIONS_CACHE_KEY not in request.session:
            request.session[settings.MAINTENANCE_NOTIFICATIONS_CACHE_KEY] = {}
        read_messages: dict = request.session[settings.MAINTENANCE_NOTIFICATIONS_CACHE_KEY]
        notice_pk: str = ser.data[get_pk_name(DjangoProjectBaseMessage)]
        notice_diff: int = ser.data["acknowledged_identifier"]
        if notice_pk not in read_messages:
            read_messages[notice_pk] = []
        diffs: list = read_messages[notice_pk]
        diffs.append(notice_diff)
        diffs = list(set(diffs))
        read_messages[notice_pk] = diffs
        request.session[settings.MAINTENANCE_NOTIFICATIONS_CACHE_KEY] = read_messages
        return Response(status=status.HTTP_201_CREATED)
