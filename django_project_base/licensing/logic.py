from typing import List

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connections, models
from django.db.models.functions import Cast
from django.utils.translation import gettext
from rest_framework.exceptions import PermissionDenied

from django_project_base.licensing.models import LicenseAccessUse

MONTHLY_ACCESS_LIMIT_IN_CURRENCY_UNITS = 5  # TODO: read from package


class LogAccessService:
    def log(self, user_profile_pk, channels: List[str], object_pk: str, on_sucess=None, **kwargs):
        # only notifications supported for now
        model_data = settings.LICENSE_ACCESS_USE_CONTENT_TYPE_MODEL.split(".")
        db_connection = "default"
        if kwargs.get("db") and kwargs["db"] != "default":
            db_connection = kwargs["db"]
            connections["default"] = connections[db_connection]

        content_type = ContentType.objects.get_for_model(model=apps.get_model(model_data[0], model_data[1]))

        content_type_model = content_type.model_class()

        current_items = LicenseAccessUse.objects.filter(user_id=str(user_profile_pk), content_type=content_type)

        _channels = list(
            content_type_model.objects.annotate(
                pkstr=Cast(content_type_model._meta.pk.name, output_field=models.CharField())
            )
            .filter(pkstr__in=current_items.values_list("content_type_object_id", flat=True))
            .values_list("sent_channels", flat=True)
        )

        ch_one = {i: _channels.count(i) for i in _channels}
        ch_two = {i: channels.count(i) for i in channels}
        from django_project_base.notifications.base.enums import ChannelIdentifier

        chl_prices = {i.name: i.notification_price for i in ChannelIdentifier.supported_channels()}
        used = 0
        for used_channel in list(set(list(ch_one.keys()) + list(ch_two.keys()))):
            used += chl_prices.get(used_channel, 0) * (ch_one.get(used_channel, 0) + ch_two.get(used_channel, 0))

        if used >= MONTHLY_ACCESS_LIMIT_IN_CURRENCY_UNITS:
            raise PermissionDenied(gettext("Your license is consumed. Please contact support."))

        if on_sucess:
            on_sucess()

        LicenseAccessUse.objects.using(db_connection).create(
            type=LicenseAccessUse.USE,
            user_id=str(user_profile_pk),
            content_type_object_id=str(object_pk).replace("-", ""),
            content_type=content_type,
        )
