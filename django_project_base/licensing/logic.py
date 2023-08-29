from typing import List

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connections
from django.db.models import Sum, Model
from django.utils.translation import gettext
from rest_framework.exceptions import PermissionDenied

from django_project_base.licensing.models import LicenseAccessUse

MONTHLY_ACCESS_LIMIT_IN_CURRENCY_UNITS = 5  # TODO: read from package


class LogAccessService:
    def log(
        self,
        user_profile_pk,
        notifications_channels_state: List[str],
        record: Model,
        item_price: float,
        comment: str,
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

        content_type = ContentType.objects.get_for_model(model=record._meta.model)

        used = LicenseAccessUse.objects.filter(user_id=str(user_profile_pk), content_type=content_type).aggregate(
            Sum("amount")
        )
        if notifications_channels_state:
            items = {i: notifications_channels_state.count(i) for i in notifications_channels_state}
            from django_project_base.notifications.base.enums import ChannelIdentifier

            chl_prices = {i.name: i.notification_price for i in ChannelIdentifier.supported_channels()}
            for used_channel in list(set(list(items.keys()))):
                used += chl_prices.get(used_channel, 0) * items.get(used_channel, 0)

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
            type=LicenseAccessUse.UseType.USE,
            user_id=str(user_profile_pk),
            content_type_object_id=str(record.pk).replace("-", ""),
            content_type=content_type,
            amount=accesses_used * item_price,
            comment=dict(comment=comment, count=accesses_used, item_price=item_price),
        )
