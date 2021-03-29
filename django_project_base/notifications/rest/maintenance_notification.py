from typing import Optional

from django.db import transaction
from django.db.models import QuerySet
from rest_framework import fields
from rest_framework.response import Response

from django_project_base.notifications.base.rest.serializer import Serializer
from django_project_base.notifications.base.rest.viewset import ViewSet
from django_project_base.notifications.models import DjangoProjectBaseNotification, DjangoProjectBaseMessage


class MessageSerializer(Serializer):
    class Meta:
        model = DjangoProjectBaseMessage
        exclude = (DjangoProjectBaseMessage._meta.pk.name,)


class MaintenanceNotificationSerializer(Serializer):
    delayed_to_timestamp = fields.SerializerMethodField()
    message = MessageSerializer()

    def get_delayed_to_timestamp(self, notification: DjangoProjectBaseNotification) -> Optional[int]:
        return int(notification.delayed_to.timestamp()) if notification and notification.delayed_to else None

    def create(self, validated_data) ->DjangoProjectBaseNotification:
        message: DjangoProjectBaseMessage = DjangoProjectBaseMessage.objects.create(**validated_data['message'])
        validated_data['message'] = message
        return super().create(validated_data)

    class Meta:
        model = DjangoProjectBaseNotification
        exclude = ()


class MaintenanceNotificationViewset(ViewSet):
    def get_serializer_class(self):
        return MaintenanceNotificationSerializer

    def get_queryset(self) -> QuerySet:
        return DjangoProjectBaseNotification.objects.maintenance_notifications()

    @transaction.atomic()
    def create(self, request, *args, **kwargs) -> Response:
        return super().create(request, *args, **kwargs)

    # add action message read
