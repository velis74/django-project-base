from typing import List

import swapper

from django.core.cache import cache
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from dynamicforms import fields
from dynamicforms.action import Actions, TableAction, TablePosition
from dynamicforms.mixins import DisplayMode
from dynamicforms.template_render.responsive_table_layout import ResponsiveTableLayout, ResponsiveTableLayouts
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.fields import IntegerField, ListField
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from django_project_base.account.constants import MERGE_USERS_QS_CK
from django_project_base.account.rest.profile import ProfileSerializer, ProfileViewSet
from django_project_base.base.permissions import IsProjectOwner, IsSuperUser
from django_project_base.utils import get_pk_name


class ProfileMergeSerializer(ProfileSerializer):
    template_context = dict(url_reverse="profile-merge-base-project")

    form_titles = {
        "table": "Merge users",
        "new": "",
        "edit": "",
    }

    actions = Actions(add_form_buttons=False)

    phone_number = fields.CharField(display=DisplayMode.HIDDEN)
    language = fields.CharField(display=DisplayMode.HIDDEN)
    email = fields.CharField(display=DisplayMode.HIDDEN)

    def __init__(self, *args, is_filter: bool = False, **kwds):
        super().__init__(*args, is_filter=is_filter, **kwds)
        self.actions.actions = (
            TableAction(
                TablePosition.ROW_END,
                label=_("Remove"),
                title=_("Remove"),
                name="delete-user",
                icon="ion-person-remove-outline",
            ),
            TableAction(
                TablePosition.HEADER,
                label=_("Merge"),
                title=_("Merge"),
                name="merge-users",
                icon="ion-git-merge-outline",
            ),
            TableAction(
                TablePosition.HEADER,
                label=_("Clear all"),
                title=_("Clear all"),
                name="clear-merge-users",
                icon="ion-remove-circle-outline",
            ),
        )

    @property
    def filter_data(self):
        return None

    class Meta(ProfileSerializer.Meta):
        responsive_columns = ResponsiveTableLayouts(
            auto_generate_single_row_layout=True,
            layouts=[
                ResponsiveTableLayout(auto_add_non_listed_columns=True),
                ResponsiveTableLayout("full_name", auto_add_non_listed_columns=False),
            ],
        )


class MergeUsersRequest(Serializer):
    users = ListField(child=IntegerField(min_value=1), required=True, allow_empty=False, min_length=2)

    def validate(self, attrs):
        MergeUserGroup = swapper.load_model("django_project_base", "MergeUserGroup")
        for user in attrs["users"]:
            if str(user) in ",".join(MergeUserGroup.objects.values_list("users", flat=True)).split(","):
                raise ValidationError(dict(users=f"Pk {user} is present in another group of users to be merged"))
        return super().validate(attrs)


class ProfileMergeViewSet(ProfileViewSet):
    serializer_class = ProfileMergeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsSuperUser | IsProjectOwner]

    schema = None

    def get_queryset(self) -> List:
        ck_val = cache.get(MERGE_USERS_QS_CK % self.request.user.pk, [])
        if not ck_val:
            return super().get_queryset().filter(pk=-1)
        return super().get_queryset().filter(pk__in=ck_val)

    def get_serializer_class(self):
        return ProfileMergeSerializer

    def get_permissions(self):
        if self.action == "clear":
            return [IsAuthenticated(), IsAdminUser()]
        else:
            return super().get_permissions()

    @transaction.atomic
    def create(self, request: Request, *args, **kwargs) -> Response:
        MergeUserGroup = swapper.load_model("django_project_base", "MergeUserGroup")
        ck = MERGE_USERS_QS_CK % self.request.user.pk
        ser = MergeUsersRequest(data=dict(users=cache.get(ck, [])))
        ser.is_valid(raise_exception=True)
        group, created = MergeUserGroup.objects.get_or_create(
            users=",".join(map(str, ser.validated_data["users"])),
            created_by=self.request.user.pk,
            project=request.selected_project,
        )
        cache.set(ck, [])
        return Response({get_pk_name(MergeUserGroup): group.pk})

    def get_current_profile(self, request: Request, **kwargs) -> Response:
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)

    def mark_current_profile_delete(self, request: Request, **kwargs) -> Response:
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, *args, **kwargs):
        pk = self.get_object().pk
        ck = MERGE_USERS_QS_CK % self.request.user.pk
        ck_val = cache.get(ck, [])
        ck_val = [i for i in ck_val if i != pk]
        cache.set(ck, list(set(ck_val)), timeout=None)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        raise APIException(code=status.HTTP_501_NOT_IMPLEMENTED)

    @action(methods=["DELETE"], detail=False, url_path="clear", url_name="clear")
    def clear(self, request: Request, **kwargs) -> Response:
        MergeUserGroup = swapper.load_model("django_project_base", "MergeUserGroup")

        cache.set(MERGE_USERS_QS_CK % self.request.user.pk, [])
        MergeUserGroup.objects.filter(created_by=self.request.user.pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
