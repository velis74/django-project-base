from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Model
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from hijack.helpers import login_user, release_hijack
from rest_framework import fields, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer


class ImpersonateRequestSerializer(Serializer):
    email = fields.EmailField(required=True)


response_schema: dict = {
    status.HTTP_200_OK: '',
    status.HTTP_403_FORBIDDEN: '',
    status.HTTP_400_BAD_REQUEST: '',
}


@extend_schema_view(
    destroy=extend_schema(exclude=True),
    create=extend_schema(exclude=True),
    update=extend_schema(exclude=True),
    list=extend_schema(exclude=True),
    retrieve=extend_schema(exclude=True),
    partial_update=extend_schema(exclude=True),
)
class ImpersonateUserViewset(viewsets.ViewSet):
    queryset = None
    serializer_class = None

    def __validate(self, req_data: dict) -> dict:
        ser: ImpersonateRequestSerializer = ImpersonateRequestSerializer(data=req_data)
        ser.is_valid(raise_exception=True)
        return ser.validated_data

    @extend_schema(
        request=ImpersonateRequestSerializer(),
        responses=response_schema,
        description='Login as another user and work on behalf of other user without having to know their credentials'
    )
    @action(detail=False, methods=['post'], url_name='impersonate-start',
            permission_classes=[IsAuthenticated, IsAdminUser])
    def start(self, request: Request) -> Response:
        validated_data: dict = self.__validate(request.data)
        hijacked_user: Model = get_object_or_404(get_user_model(), email=validated_data['email'])
        if request.user == hijacked_user:
            raise PermissionDenied(_('Impersonating self is not allowed'))
        login_user(request, hijacked_user)
        return Response()

    @extend_schema(
        responses=response_schema,
        description='Logout as another user'
    )
    @action(detail=False, methods=['post'], url_name='impersonate-end', permission_classes=[IsAuthenticated])
    def end(self, request: Request) -> Response:
        release_hijack(request)
        return Response()

    def list(self, request: Request) -> None:
        pass

    def create(self, request: Request) -> None:
        pass

    def retrieve(self, request: Request, pk: Any = None) -> None:
        pass

    def update(self, request: Request, pk: Any = None) -> None:
        pass

    def partial_update(self, request: Request, pk: Any = None) -> None:
        pass

    def destroy(self, request: Request, pk: Any = None) -> None:
        pass
