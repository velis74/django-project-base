from collections.abc import Iterable

import pytz
import swapper

from django.conf import settings
from django.db import models
from django.db.models import Case, F, Prefetch, QuerySet, Value, When
from django.db.models.functions import Coalesce, Concat, NullIf, Trim
from django.db.models.lookups import IsNull
from django.utils.dateparse import (
    datetime_re,
    iso8601_duration_re,
    parse_datetime,
    parse_duration,
    parse_time,
    standard_duration_re,
    time_re,
)
from django.utils.timezone import datetime, now, timedelta
from dynamicforms import fields
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request

from django_project_base.account.middleware import ProjectNotSelectedError
from django_project_base.base.permissions import is_superuser


def annotate_with_full_name(queryset, field, reverse=False):
    if reverse:
        first = "last_name"
        last = "first_name"
    else:
        first = "first_name"
        last = "last_name"
    annotation = {
        field: Case(
            # Če sta first_name in last_name prazna ali NULL
            When(
                IsNull(NullIf(F(first), Value("")), rhs=True) & IsNull(NullIf(F(last), Value("")), rhs=True),
                then=Coalesce(
                    NullIf(F("username"), Value("")),
                    NullIf(F("email"), Value("")),
                ),
            ),
            # Sicer first_name + presledek + last_name (trim obeh)
            default=Trim(
                Concat(
                    Trim(F(first)),
                    Value(" "),
                    Trim(F(last)),
                )
            ),
            output_field=models.CharField(),
        ),
    }
    return queryset.annotate(**annotation)


def get_project_members(request: Request, project=None, profile_model=None) -> QuerySet:
    project = project or request.selected_project
    try:
        project_members = swapper.load_model("django_project_base", "ProjectMember").objects.filter(project_id=project)
    except ProjectNotSelectedError:
        project = None
        project_members = swapper.load_model("django_project_base", "ProjectMember").objects.all()
        if not is_superuser(request.user):
            raise PermissionDenied("Project not selected")

    profile_model = profile_model or swapper.load_model("django_project_base", "Profile")

    qs = profile_model.objects.prefetch_related(
        Prefetch("projects", queryset=project_members), "groups", "user_permissions"
    )
    qs = annotate_with_full_name(qs, "un")
    qs = annotate_with_full_name(qs, "un_sort", reverse=True)
    qs = qs.exclude(delete_at__isnull=False, delete_at__lt=now())

    if project is not None:
        # if current project was parsed from request, filter profiles to current project only
        qs = qs.filter(projects__project=project)
    else:
        qs = qs.none()

    if request.query_params.get("remove-merge-users", "false") in fields.BooleanField.TRUE_VALUES:
        MergeUserGroup = swapper.load_model("django_project_base", "MergeUserGroup")
        exclude_qs = set()
        for mgu in MergeUserGroup.objects.filter(created_by=request.user.pk).values_list("users", flat=True).all():
            if mgu and mgu.split(","):
                exclude_qs.update(map(int, mgu.split(",")))
        if exclude_qs:
            qs = qs.exclude(pk__in=exclude_qs)

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
    if field == "user_groups":
        if isinstance(value, Iterable):
            return queryset.filter(members__user_group__in=value)
        return queryset.filter(members__user_group=value)

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
            start = datetime.combine(now().date(), parse_time(value).replace(microsecond=0))
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
