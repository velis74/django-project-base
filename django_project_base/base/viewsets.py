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

    model = None

    def get_queryset(self):
        return filter_queryset_or_model_to_project(self.queryset, self.model, self.request.selected_project)
