from dynamicforms.viewsets import ModelViewSet
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer

from django_project_base.notifications.models import DjangoProjectBaseNotification
from django_project_base.notifications.rest.maintenance_notification import MessageSerializer


class NotificationSerializer(ModelSerializer):
    message = MessageSerializer()

    class Meta:
        model = DjangoProjectBaseNotification
        exclude = ("content_entity_context",)


class NotificationViewset(ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return NotificationSerializer

    def get_queryset(self):
        return DjangoProjectBaseNotification.objects.all()
