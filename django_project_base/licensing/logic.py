from typing import List

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connections
from django.db.models import Model, Sum
from django.utils.translation import gettext
from dynamicforms import fields
from dynamicforms.serializers import Serializer
from rest_framework.exceptions import PermissionDenied

from django_project_base.licensing.models import LicenseAccessUse

MONTHLY_ACCESS_LIMIT_IN_CURRENCY_UNITS = 86.97  # TODO: read from package


class LicenseUsageReport(Serializer):
    item = fields.CharField(read_only=True)
    usage_sum = fields.FloatField(read_only=True)


class LicenseReportSerializer(Serializer):
    credit = fields.FloatField(read_only=True)
    used_credit = fields.FloatField(read_only=True)
    remaining_credit = fields.FloatField(read_only=True)

    usage_report = fields.ListField(child=LicenseUsageReport(), allow_empty=True, read_only=True)


class LogAccessService:
    def report(self, user: Model) -> dict:
        used = (
            LicenseAccessUse.objects.filter(user_id=str(user.pk), amount__isnull=False, amount__gt=0)
            .values("content_type")
            .annotate(count=Sum("amount"))
            .order_by("-amount")
        )
        usage_report = []
        added_types = []
        for agg in used:
            if (
                content_type := ContentType.objects.get(pk=agg["content_type"])
            ) and content_type.model_class()._meta.verbose_name not in added_types:
                usage_report.append({"item": content_type.model_class()._meta.verbose_name, "usage_sum": agg["count"]})
                added_types.append(content_type.model_class()._meta.verbose_name)
        used_credit = 0
        if cnt := used.first():
            used_credit = cnt["count"]
        return LicenseReportSerializer(
            {
                "credit": MONTHLY_ACCESS_LIMIT_IN_CURRENCY_UNITS,
                "used_credit": used_credit,
                "usage_report": usage_report,
                "remaining_credit": MONTHLY_ACCESS_LIMIT_IN_CURRENCY_UNITS - used_credit,
            }
        ).data

    def log(
        self,
        user_profile_pk,
        notifications_channels_state: List[str],
        record: Model,
        item_price: float,
        comment: str,
        on_sucess=None,
        **kwargs,
    ):
        if getattr(settings, "TESTING", False) and on_sucess:
            on_sucess()
            return

        db_connection = "default"
        if kwargs.get("db") and kwargs["db"] != "default":
            db_connection = kwargs["db"]
            connections["default"] = connections[db_connection]

        content_type = ContentType.objects.get_for_model(model=record._meta.model)

        used = (
            LicenseAccessUse.objects.filter(user_id=str(user_profile_pk), content_type=content_type)
            .aggregate(Sum("amount"))
            .get("amount__sum", None)
            or 0
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
