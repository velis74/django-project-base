from typing import List, Optional

from django.contrib.contenttypes.models import ContentType
from django.db import connections
from django.db.models import Model, Sum
from django.utils.translation import gettext, gettext_lazy as _
from dynamicforms import fields
from dynamicforms.serializers import Serializer
from rest_framework.exceptions import PermissionDenied

from django_project_base.licensing.models import LicenseAccessUse


class LicenseUsageReport(Serializer):
    item = fields.CharField(read_only=True, label=_("Type"))
    usage_sum = fields.FloatField(read_only=True, label=_("Used"))


class LicenseReportSerializer(Serializer):
    credit = fields.FloatField(read_only=True, label=_("Credit"))
    used_credit = fields.FloatField(read_only=True, label=_("Used credit"))
    remaining_credit = fields.FloatField(read_only=True, label=_("Remaining credit"))

    usage_report = fields.ListField(
        child=LicenseUsageReport(), allow_empty=True, read_only=True, label=_("Usage report")
    )


class LogAccessService:
    db = "default"

    def __init__(self, db: Optional[str] = None) -> None:
        super().__init__()
        if db:
            self.db = db

    def _user_access_user_inflow(self, user_id) -> float:
        return abs(
            LicenseAccessUse.objects.using(self.db)
            .filter(user_id=str(user_id), amount__lt=0)
            .aggregate(Sum("amount"))
            .get("amount__sum", None)
            or 0
        )

    def report(self, user: Model) -> dict:
        user_query = LicenseAccessUse.objects.using(self.db).filter(
            user_id=str(user.pk), amount__isnull=False, amount__gt=0
        )

        usage_report = []
        added_types = []
        for agg in user_query.values("content_type").annotate(count=Sum("amount")):
            if (
                content_type := ContentType.objects.using(self.db).get(pk=agg["content_type"])
            ) and content_type.model_class()._meta.verbose_name not in added_types:
                usage_report.append(
                    {"item": content_type.model_class()._meta.verbose_name, "usage_sum": round(agg.get("count", 0), 2)}
                )
                added_types.append(content_type.model_class()._meta.verbose_name)
        used_credit = 0
        if user_query.exists():
            used_credit = round(user_query.aggregate(count=Sum("amount")).get("count", 0), 4)

        credit = self._user_access_user_inflow(user.pk)

        return LicenseReportSerializer(
            {
                "credit": round(credit, 2),
                "used_credit": used_credit,
                "usage_report": usage_report,
                "remaining_credit": round(credit - used_credit, 4),
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
    ) -> int:
        connections["default"] = connections[self.db]
        content_type = ContentType.objects.get_for_model(model=record._meta.model)
        used = (
            LicenseAccessUse.objects.using(self.db)
            .filter(user_id=str(user_profile_pk), content_type=content_type)
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

        if not kwargs.get("is_system_notification") and used >= 0:
            raise PermissionDenied(gettext("Your license is consumed. Please contact support."))

        if on_sucess:
            accesses_used = on_sucess()
        else:
            accesses_used = 1

        amount = accesses_used * item_price

        LicenseAccessUse.objects.using(self.db).create(
            type=LicenseAccessUse.UseType.USE,
            user_id=str(user_profile_pk),
            content_type_object_id=str(record.pk).replace("-", ""),
            content_type=content_type,
            amount=amount,
            comment=dict(comment=comment, count=accesses_used, item_price=item_price, sender=kwargs.get("sender", "")),
        )

        return accesses_used
