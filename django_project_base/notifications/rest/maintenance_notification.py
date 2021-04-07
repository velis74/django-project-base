import datetime
from distutils.util import strtobool
from typing import Optional

from django.conf import settings
from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from pytz import UTC
from rest_framework import fields, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer as RestFrameworkSerializer

from django_project_base.notifications.base.enums import NotificationType
from django_project_base.notifications.base.rest.serializer import Serializer
from django_project_base.notifications.base.rest.viewset import ViewSet
from django_project_base.notifications.models import DjangoProjectBaseNotification, DjangoProjectBaseMessage
from django_project_base.notifications.utils import utc_now


def _is_model_field_null(model: 'Model', field_name: str) -> bool:
    return next(filter(lambda c: c.name == field_name, model._meta.fields)).null


class NotificationAcknowledgedRequestSerializer(RestFrameworkSerializer):

    def __new__(cls, *args, **kwargs):
        new: 'NotificationAcknowledgedRequestSerializer' = super().__new__(cls, *args, **kwargs)
        new.fields[DjangoProjectBaseMessage._meta.pk.name] = fields.UUIDField(required=True, allow_null=False)
        new.fields['acknowledged_identifier'] = fields.IntegerField(required=True, allow_null=False)
        return new

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UTCDateTimeField(fields.DateTimeField):

    def enforce_timezone(self, value):
        return value


class MessageSerializer(Serializer):
    class Meta:
        model = DjangoProjectBaseMessage
        exclude = (DjangoProjectBaseMessage._meta.pk.name,)


class MaintenanceNotificationSerializer(Serializer):
    delayed_to_timestamp = fields.SerializerMethodField()
    notification_acknowledged_data = fields.SerializerMethodField()
    message = MessageSerializer()
    type = fields.CharField(required=False, allow_null=True, default=NotificationType.MAINTENANCE.value)

    created_at = UTCDateTimeField(read_only=True)
    sent_at = UTCDateTimeField(
        required=not _is_model_field_null(DjangoProjectBaseNotification, 'sent_at'),
        allow_null=_is_model_field_null(DjangoProjectBaseNotification, 'sent_at'))
    delayed_to = UTCDateTimeField(
        required=not _is_model_field_null(DjangoProjectBaseNotification, 'delayed_to'),
        allow_null=_is_model_field_null(DjangoProjectBaseNotification, 'delayed_to'))

    def get_delayed_to_timestamp(self, notification: DjangoProjectBaseNotification) -> Optional[int]:
        return int(notification.delayed_to.timestamp()) if notification and notification.delayed_to else None

    def get_notification_acknowledged_data(self, notification: DjangoProjectBaseNotification) -> list:
        request: Optional[Request] = self.context.get('request')
        return request.session.get(settings.MAINTENENACE_NOTIFICATIONS_CACHE_KEY, {}).get(str(notification.pk), [])

    def create(self, validated_data) -> DjangoProjectBaseNotification:
        message: DjangoProjectBaseMessage = DjangoProjectBaseMessage.objects.create(**validated_data['message'])
        validated_data['message'] = message
        if not validated_data['type']:
            validated_data['type'] = NotificationType.MAINTENANCE.value
        return super().create(validated_data)

    # todo: update and partial update, destroy

    def validate(self, attrs: dict):
        _type: Optional[str] = attrs.get('type')
        if _type and _type != NotificationType.MAINTENANCE.value:
            raise ValidationError({'type': 'Only type %s allowed.' % NotificationType.MAINTENANCE.value})
        time_delta: datetime.timedelta = datetime.timedelta(
            seconds=settings.TIME_BUFFER_FOR_CURRENT_MAINTENANCE_API_QUERY)
        existing_maintenances: list = DjangoProjectBaseNotification.objects.filter(
            delayed_to__range=[attrs['delayed_to'] - time_delta, attrs['delayed_to'] + time_delta])
        if bool(len(existing_maintenances)):
            proposed_maintenance_time_utc: datetime = existing_maintenances[
                                                          len(existing_maintenances) - 1].delayed_to + time_delta
            raise ValidationError(
                {'delayed_to': 'Another maintenance is planned at this time. Plan maintenance after %s UTC' % str(
                    proposed_maintenance_time_utc)})
        if attrs['delayed_to'].tzinfo != UTC:
            raise ValidationError(dict(delayed_to='Delayed to must be in UTC timezone'))

        return super().validate(attrs)

    class Meta:
        model = DjangoProjectBaseNotification
        exclude = ('required_channels', 'sent_channels', 'failed_channels', 'recipients', 'level',)


@extend_schema_view(
    destroy=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
)
class UsersMaintenanceNotificationViewset(ViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return MaintenanceNotificationSerializer

    def get_queryset(self) -> list:
        return DjangoProjectBaseNotification.objects.maintenance_notifications()

    @extend_schema(
        request=MaintenanceNotificationSerializer(),
        description='Create maintenance notification'
    )
    @transaction.atomic
    def create(self, request: Request, *args, **kwargs) -> Response:
        return super().create(request, *args, **kwargs)

    def list(self, request: Request, *args, **kwargs) -> Response:
        if bool(strtobool(request.query_params.get('current', 'False'))):
            now: datetime.datetime = utc_now()
            time_delta: datetime.timedelta = datetime.timedelta(
                seconds=settings.TIME_BUFFER_FOR_CURRENT_MAINTENANCE_API_QUERY)
            current_maintenance: Optional[DjangoProjectBaseNotification] = next(
                iter(DjangoProjectBaseNotification.objects.filter(
                    delayed_to__range=[now - time_delta, now + time_delta])), None)
            return Response(self.get_serializer(current_maintenance, many=False).data)
        read_notifications: dict = request.session.get(settings.MAINTENENACE_NOTIFICATIONS_CACHE_KEY, {})
        pk_name: str = DjangoProjectBaseMessage._meta.pk.name
        return Response(self.get_serializer(
            filter(lambda n: len(read_notifications.get(str(getattr(n, pk_name)), [])) < 3, self.get_queryset()),
            many=True).data)

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
        description='Mark message as acknowledged by user'
    )
    @action(methods=['POST'], detail=False, url_path='acknowledged', url_name='acknowledged')
    def acknowledged(self, request: Request, **kwargs) -> Response:
        # todo: storage for acknowledged notifications should be configurable
        ser: NotificationAcknowledgedRequestSerializer = NotificationAcknowledgedRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        if settings.MAINTENENACE_NOTIFICATIONS_CACHE_KEY not in request.session:
            request.session[settings.MAINTENENACE_NOTIFICATIONS_CACHE_KEY] = {}
        read_messages: dict = request.session[settings.MAINTENENACE_NOTIFICATIONS_CACHE_KEY]
        notice_pk: str = ser.data[DjangoProjectBaseMessage._meta.pk.name]
        notice_diff: int = ser.data['acknowledged_identifier']
        if notice_pk not in read_messages:
            read_messages[notice_pk] = []
        diffs: list = read_messages[notice_pk]
        diffs.append(notice_diff)
        diffs = list(set(diffs))
        read_messages[notice_pk] = diffs
        request.session[settings.MAINTENENACE_NOTIFICATIONS_CACHE_KEY] = read_messages
        return Response()
