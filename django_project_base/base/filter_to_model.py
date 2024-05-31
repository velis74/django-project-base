"""
Project base expects there to be a project and nearly everything else is linked to the project.
Hence this file that offers filtering models and queries by (currently selected) project

There are three utility functions here:

filter_queryset_to_project:
  filters queryset on specified project field or subquery to the given project.
  if no project can be found, empty queryset is returned

filter_queryset_or_model_to_project:
  expands on filter_queryset_to_project and includes smart handling either models or querysets

ProjectFilteringManager:
  a Manager that adds a filter_by_project method to filter model records.
  Easily accessible by setting model objects to it

This file is the basis for viewsets.py ProjectFilteringViewSet
"""

from typing import Optional, Type, TYPE_CHECKING

from django.db.models import Manager, Model, QuerySet

if TYPE_CHECKING:
    from django_project_base.base.models import BaseProject


def filter_queryset_to_project(
    queryset: QuerySet, project_field: str = "project", project: "BaseProject" = None
) -> QuerySet:
    from django_project_base.account.middleware import ProjectNotSelectedError
    from django_project_base.base.middleware import get_current_request, has_current_request

    if not project and has_current_request():
        project = getattr(get_current_request(), "selected_project", None)

    try:
        if project:
            return queryset.filter(**{project_field: project})
    except ProjectNotSelectedError:
        pass
    return queryset.none()


def filter_queryset_or_model_to_project(
    queryset: Optional[QuerySet] = None,
    model: Optional[Type[Model]] = None,
    project_field: str = "project",
    project: Optional["BaseProject"] = None,
) -> QuerySet:
    if model is not None and not hasattr(model, "objects") and callable(model):
        model = model()

    if hasattr(queryset, "filter_by_project"):
        # if the provided queryset is already of the correct manager sort
        objs = queryset
    elif queryset is not None:
        # a queryset has been provided and it needs to be filtered
        return filter_queryset_to_project(queryset, project_field, project)
    elif model is None:
        raise ValueError("ProjectFilteringViewSet requires either queryset or model to be set")
    elif isinstance(model.objects, ProjectFilteringManager):
        # then we check if the provided model has the correct manager
        objs = model.objects
    else:
        # finally we filter the queryset of the provided model
        return filter_queryset_to_project(model.objects, project_field, project)

    return objs.filter_by_project(project)


class ProjectFilteringManager(Manager):
    """
    Manager that allows for filtering model queryset to a specified project records only
    """

    def __init__(self, project_field: str = "project"):
        super().__init__()
        self.project_field = project_field

    def filter_by_project(self, project: "BaseProject" = None):
        return filter_queryset_to_project(self.get_queryset(), self.project_field, project)
