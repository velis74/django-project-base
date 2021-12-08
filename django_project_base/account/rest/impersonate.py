from django.contrib.auth import get_user_model
from django.db.models import Model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from dynamicforms import fields, serializers, viewsets
from dynamicforms.action import Actions, FormButtonAction, FormButtonTypes
from dynamicforms.mixins import DisplayMode
from hijack.helpers import login_user, release_hijack
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response


class ImpersonateRequestSerializer(serializers.Serializer):
    id = fields.IntegerField(required=False)
    email = fields.EmailField(required=False)
    username = fields.CharField(required=False)


class ImpersonateUserDialogSerializer(serializers.Serializer):
    template_context = dict(url_reverse='profile-base-impersonate-user',
                            dialog_header_classes='bg-info')
    form_titles = {
        'table': '',
        'new': 'Search for user',
        'edit': '',
    }

    # TODO: Trenutno je narejena samo komponenta. HTML dialog pa ne... ali je to v redu?
    form_template = 'accounts/impersonate_dialog.html'

    # TODO: Placeholderja še ni... je samo predviden v komponentah... ampak se še nikjer ne definira
    # TODO: Trenutno se polje na roko definira na custom layoutu. Treba je podpreti, da bo tudi standardni input
    #  podpiral autocomplete
    user = fields.CharField(label='')
    user_id = fields.IntegerField(label='', display=DisplayMode.INVISIBLE)

    actions = Actions(FormButtonAction(btn_type=FormButtonTypes.CANCEL, name='cancel'),
                      FormButtonAction(btn_type=FormButtonTypes.SUBMIT, name='submit', label=_('Select')),
                      add_form_buttons=False)


@extend_schema_view(
    create=extend_schema(exclude=True),
    retrieve=extend_schema(exclude=True),
)
class ImpersonateUserViewset(viewsets.SingleRecordViewSet):
    serializer_class = ImpersonateUserDialogSerializer

    def new_object(self):
        return dict(user='', user_id=0)

    # noinspection PyMethodMayBeStatic
    def __validate(self, req_data: dict) -> dict:
        ser: ImpersonateRequestSerializer = ImpersonateRequestSerializer(data=req_data)
        ser.is_valid(raise_exception=True)
        return ser.validated_data

    @extend_schema(
        request=ImpersonateRequestSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK', ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(
                description='Forbidden. You do not have permission to perform '
                            'this action. or Impersonating self is not allowed')
        },
        description='Login as another user and work on behalf of other user without having to know their credentials'
    )
    @action(detail=False, methods=['post'], url_name='impersonate-start',
            permission_classes=[IsAuthenticated, IsAdminUser])
    def start(self, request: Request) -> Response:
        validated_data: dict = self.__validate(request.data)
        hijacked_user: Model = get_object_or_404(get_user_model(), **validated_data)
        if request.user == hijacked_user:
            raise PermissionDenied(_('Impersonating self is not allowed'))
        login_user(request, hijacked_user)
        return Response()

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(description='OK'),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Forbidden')
        },
        description='Logout as another user'
    )
    @action(detail=False, methods=['post'], url_name='impersonate-end', permission_classes=[IsAuthenticated])
    def end(self, request: Request) -> Response:
        release_hijack(request)
        return Response()

    def create(self, request: Request, *args, **kwargs) -> None:
        pass
