"""
A ModelViewSet base to provide automatic filtering based on currently selected project
"""

from dynamicforms.viewsets import ModelViewSet

from django_project_base.base.filter_to_model import filter_queryset_or_model_to_project


class ProjectFilteringViewSet(ModelViewSet):
    """
    ViewSet that automatically performs filtering on project for the given model

    You may provide a queryset, just like in standard DRF ViewSets
    You may as well provide a model class that will be used instead of the queryset.
    The model instance may also be a callable that will return a model class when called (for deferred resolution)
    """
    pagination_class = ModelViewSet.generate_paged_loader(ordering=["id"])

    model = None
    project_field = None

    def get_queryset(self):
        return filter_queryset_or_model_to_project(
            self.queryset, self.model, self.project_field or "project", self.request.selected_project
        )
