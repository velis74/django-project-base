from typing import List

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connections, models
from django.db.models.functions import Cast
from django.utils.translation import gettext
from rest_framework.exceptions import PermissionDenied

from django_project_base.licensing.models import LicenseAccessUse
from django_project_base.utils import get_pk_name

MONTHLY_ACCESS_LIMIT_IN_CURRENCY_UNITS = 5  # TODO: read from package


class LogAccessService:
    def log(
        self,
        user_profile_pk,
        channels: List[str],
        object_pk: str,
        channel_price: float,
        channel: str,
        on_sucess=None,
        **kwargs
    ):
        if getattr(settings, "TESTING", False) and on_sucess:
            on_sucess()
            return

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
                pkstr=Cast(get_pk_name(content_type_model), output_field=models.CharField())
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

        allowed_users = getattr(settings, "NOTIFICATIONS_ALLOWED_USERS", [])
        if not allowed_users:
            allowed_users = getattr(kwargs.get("settings", object()), "NOTIFICATIONS_ALLOWED_USERS", [])

        if str(user_profile_pk) not in list(map(str, allowed_users)):
            raise PermissionDenied

        if used >= MONTHLY_ACCESS_LIMIT_IN_CURRENCY_UNITS:  # janez medja
            raise PermissionDenied(gettext("Your license is consumed. Please contact support."))

        accesses_used = 1
        if on_sucess:
            on_success = on_sucess()
            if on_success:
                accesses_used = on_success

        LicenseAccessUse.objects.using(db_connection).create(
            type=LicenseAccessUse.USE,
            user_id=str(user_profile_pk),
            content_type_object_id=str(object_pk).replace("-", ""),
            content_type=content_type,
            amount=accesses_used * channel_price,
            comment=dict(channel=channel, count=accesses_used),
        )
