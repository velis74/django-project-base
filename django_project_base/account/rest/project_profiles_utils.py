from datetime import datetime, timedelta

import pytz
import swapper
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models import Case, CharField, Prefetch, QuerySet, Value, When
from django.db.models.functions import Coalesce, Concat
from django.utils.dateparse import (
    datetime_re,
    iso8601_duration_re,
    parse_datetime,
    parse_duration,
    parse_time,
    standard_duration_re,
    time_re,
)
from dynamicforms import fields
from rest_framework.request import Request

from django_project_base.account.constants import MERGE_USERS_QS_CK
from django_project_base.account.middleware import ProjectNotSelectedError


def get_project_members(request: Request, project=None) -> QuerySet:
    project = project or request.selected_project
    try:
        project_members = swapper.load_model("django_project_base", "ProjectMember").objects.filter(project_id=project)
    except ProjectNotSelectedError:
        project = None
        project_members = swapper.load_model("django_project_base", "ProjectMember").objects.all()
    qs = (
        swapper.load_model("django_project_base", "Profile")
        .objects.prefetch_related(Prefetch("projects", queryset=project_members), "groups", "user_permissions")
        .annotate(
            un=Concat(
                Coalesce(
                    Case(When(first_name="", then="username"), default="first_name", output_field=CharField()),
                    Value(""),
                ),
                Value(" "),
                Coalesce(
                    Case(When(last_name="", then="username"), default="last_name", output_field=CharField()),
                    "username",
                ),
            ),
            un_sort=Concat(
                Coalesce(
                    Case(When(last_name="", then="username"), default="last_name", output_field=CharField()),
                    "username",
                ),
                Value(" "),
                Coalesce(
                    Case(When(first_name="", then="username"), default="first_name", output_field=CharField()),
                    Value(""),
                ),
            ),
        )
    )

    qs = qs.exclude(delete_at__isnull=False, delete_at__lt=datetime.now())

    if project is not None:
        # if current project was parsed from request, filter profiles to current project only
        qs = qs.filter(projects__project=project)
    elif not (request.user.is_staff or request.user.is_superuser):
        # but if user is not an admin, and the project is not known, only return this user's project
        qs = qs.filter(pk=request.user.pk)

    if request.query_params.get("remove-merge-users", "false") in fields.BooleanField.TRUE_VALUES:
        MergeUserGroup = swapper.load_model("django_project_base", "MergeUserGroup")
        exclude_qs = list(
            map(
                str,
                list(MergeUserGroup.objects.filter(created_by=request.user.pk).values_list("users", flat=True))
                + cache.get(MERGE_USERS_QS_CK % request.user.pk, []),  # noqa: W503
            )
        )
        if exclude_qs:
            qs = qs.exclude(pk__in=map(int, exclude_qs))

    qs = qs.order_by("un", "id")
    return qs.distinct()


def __get_time_resolution(value: str) -> dict:
    try:
        value = value.replace("Z", "")
        resolution = (
            getattr(time_re.match(value), "lastgroup", "")
            or getattr(datetime_re.match(value), "lastgroup", "")
            or getattr(standard_duration_re.match(value), "lastgroup", "")
            or getattr(iso8601_duration_re.match(value), "lastgroup", "")
        )
        if resolution in ("second", "microsecond", "seconds", "microseconds"):
            return dict(seconds=1)
        if resolution in ("hour", "hours"):
            return dict(hours=1)
        if resolution in ("minute", "minutes"):
            return dict(minutes=1)
    except:
        pass
    return {}


def filter_project_members_fields(queryset: QuerySet, field: str, value) -> QuerySet:
    if value is None or value == "":
        return queryset

    if field == "full_name":
        return queryset.filter(un__icontains=value)
    if field == "state":
        return queryset.filter(projects__state=value)

    model_meta = queryset.model._meta

    if field not in (fld.name for fld in model_meta.get_fields()):
        return queryset

    try:
        # TODO: this would probably be better moved into the fields themselves
        if isinstance(model_meta.get_field(field), (models.CharField, models.TextField)):
            return queryset.filter(**{field + "__icontains": value})
        if isinstance(model_meta.get_field(field), (models.DateTimeField,)):
            date_time: datetime = parse_datetime(value.replace("Z", ""))
            date_time.replace(microsecond=0)
            date_time = pytz.timezone(settings.TIME_ZONE).localize(date_time).astimezone(pytz.utc)
            return queryset.filter(
                **{
                    field + "__gte": date_time,
                    field + "__lt": date_time + timedelta(**__get_time_resolution(value)),
                }
            )
        if isinstance(model_meta.get_field(field), (models.TimeField,)):
            start = datetime.combine(datetime.now().date(), parse_time(value).replace(microsecond=0))
            end = (start + timedelta(**__get_time_resolution(value))).time()
            return queryset.filter(**{field + "__gte": start, field + "__lt": end})
        if isinstance(model_meta.get_field(field), (models.DurationField,)):
            duration = parse_duration(value)
            duration = duration - timedelta(microseconds=duration.microseconds)
            return queryset.filter(
                **{
                    field + "__gte": duration,
                    field + "__lt": duration + timedelta(**__get_time_resolution(value)),
                }
            )
        if isinstance(model_meta.get_field(field), (models.DateField,)):
            date_time = None
            for date_time_fmt in [settings.DATE_FORMAT, "%Y-%m-%d"]:
                try:
                    date_time = datetime.strptime(value, date_time_fmt)
                    break
                except:
                    pass
            date_time = pytz.timezone(settings.TIME_ZONE).localize(date_time).astimezone(pytz.utc)
            return queryset.filter(**{field + "__gte": date_time, field + "__lt": date_time + timedelta(days=1)})
        else:
            if isinstance(model_meta.get_field(field), models.BooleanField):
                value = value == "true"
            return queryset.filter(**{field: value})
    except:
        return queryset
