import socket

from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from dynamicforms import viewsets
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS

from docs.api_docs.no_df_prev_id_auto_schema import NoDfPrevIdAutoSchema
from main.models import InternalMail
from main.rest_df.internal_mail.serializers.internal_mail_serializer import InternalMailSerializer
from main.rest_df.is_admin_or_super_user_permission import IsAdminOrSuperUserPermission
from main.rest_df.viewsets.mars_viewset import MarsViewSet


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class InternalMailViewSet(MarsViewSet):
    """
    Internal mails system, functionality to reduce load on Zoho Mail for development environments
    """
    permission_classes = (IsAuthenticated, IsAdminOrSuperUserPermission, ReadOnly)
    pagination_class = viewsets.ModelViewSet.generate_paged_loader(ordering='-created_at')  # enables pagination

    serializer_class = InternalMailSerializer
    swagger_schema = NoDfPrevIdAutoSchema

    def get_queryset(self):
        return InternalMail.objects.filter(origin_server=socket.gethostname().lower())

    @method_decorator(name='list', decorator=swagger_auto_schema(
        operation_description="Lists internal mail records.",
        responses={
            status.HTTP_200_OK: openapi.Response('Response', InternalMailSerializer),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
        }, operation_id='list-internal-mail-objects',
    ))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(name='retrieve', decorator=swagger_auto_schema(
        operation_description="Displays record data for primary key.",
        responses={
            status.HTTP_200_OK: openapi.Response('Response for record', InternalMailSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response('Not found'),
            status.HTTP_403_FORBIDDEN: openapi.Response('Forbidden'),
        }, operation_id='retrieve-internal-mail-object'
    ))
    def retrieve(self: viewsets.ModelViewSet, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
