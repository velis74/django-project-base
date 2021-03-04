from rest_framework import fields

from django_project_base.notifications.base.rest.serializer import Serializer
from django_project_base.notifications.base.rest.viewset import ViewSet
from django_project_base.notifications.models import DjangoProjectBaseNotification


class MaintenanceNotificationSerializer(Serializer):
    delayed_to_timestamp = fields.SerializerMethodField()

    def get_delayed_to_timestamp(self, notification: DjangoProjectBaseNotification):
        return int(notification.delayed_to.timestamp()) if notification and notification.delayed_to else None

    class Meta:
        model = DjangoProjectBaseNotification
        exclude = ()


class MaintenanceNotificationViewset(ViewSet):
    def get_serializer_class(self):
        return MaintenanceNotificationSerializer

    def get_queryset(self):
        return DjangoProjectBaseNotification.objects.maintenance_notifications()

    # add action message read
