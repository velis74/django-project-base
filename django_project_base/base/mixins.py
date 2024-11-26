from typing import Dict, List, TYPE_CHECKING, Union

from django.core.exceptions import FieldDoesNotExist

if TYPE_CHECKING:
    from dynamicforms.serializers import Serializer


class ProjectMixin:
    """
    Use this mixin in serializers that contains project field. Mixin will show project field based on
    DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE setting. It will also make sure that user can only select within
    permitted projects if DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE is set to PROMPT.
    """

    PROJECT_FIELD = "project"

    # noinspection PyMethodMayBeStatic
    def should_show_project_field(self: Union["Serializer", "ProjectMixin"]):
        """
        Project field is shown only if DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE is set to PROMPT and user is permitted
        to more than one project.
        """
        from django_project_base.project_selection import get_selected_project_mode, get_user_project
        from django_project_base.project_selection_constants import SelectedProjectMode

        if get_selected_project_mode() == SelectedProjectMode.PROMPT:
            if request := self.context.get("request", None):
                if get_user_project(request.user):
                    return False
            return True
        else:
            return False

    def get_project_fields(self: Union["Serializer", "ProjectMixin"]):
        """
        Returns all fields that refers to project in serializer. Default field is "project".
        If field name is different in project, override this attribute in serializer.
        Attribute can be str or list of strs, if there are multiple fields, that are referring to project in serializer
        """
        project_field = getattr(self, "PROJECT_FIELD", None)
        if isinstance(project_field, str):
            ret = [project_field]
        elif isinstance(project_field, list):
            ret = project_field
        else:
            raise Exception("PROJECT_FIELD attribute of serializer must be a str or list of strs")

        declared_fields = list(self._declared_fields.keys())
        model_fields = [_fld.name for _fld in self.Meta.model._meta.get_fields()]
        for fld in ret:
            if fld not in declared_fields + model_fields:
                raise Exception(f"field {fld} not valid field in serializer")
        return ret

    def get_available_projects(self: Union["Serializer", "ProjectMixin"]):
        """
        Returns queryset of project that user can choose from on form
        """
        from django_project_base.project_selection import get_user_projects

        user = None
        if request := self.context.get("request", None):
            user = request.user
        return get_user_projects(user)

    def build_relational_field(self: Union["Serializer", "ProjectMixin"], field_name, relation_info):
        """
        Overridden DRF function where we use ProjectField class for fields that are referring to project, but are not
        declared in serializer
        """
        from django_project_base.base.fields import ProjectField

        field_class, field_kwargs = super().build_relational_field(field_name, relation_info)
        if field_name in self.get_project_fields():
            field_class = ProjectField
        return field_class, field_kwargs

    def get_uniqueness_extra_kwargs(
        self: Union["Serializer", "ProjectMixin"], field_names: List[str], declared_fields: Dict, extra_kwargs: Dict
    ):
        """
        Overridden DRF function where we set/prepare display and queryset attribute for project fields
        """
        from dynamicforms.mixins import DisplayMode

        from django_project_base.base.fields import ProjectField
        from django_project_base.base.models import get_project_model

        if self.should_show_project_field():
            project_display_mode = DisplayMode.FULL
            queryset = self.get_available_projects()
        else:
            project_display_mode = DisplayMode.HIDDEN
            queryset = get_project_model().objects.none()

        for project_field in self.get_project_fields():
            s_field = declared_fields.get(project_field, getattr(self, project_field, None))
            if s_field and isinstance(s_field, ProjectField):
                s_field.set_field_attrs(display=project_display_mode, queryset=queryset)
                continue
            try:
                # noinspection PyProtectedMember
                d_field = self.Meta.model._meta.get_field(project_field)
            except FieldDoesNotExist:
                d_field = None

            if d_field:
                extra = extra_kwargs.get(project_field, dict())

                if "display" not in extra:
                    extra.setdefault("display_form", project_display_mode)
                    extra.setdefault("display_table", project_display_mode)
                if "queryset" not in extra:
                    extra.setdefault("queryset", queryset)
                extra_kwargs[project_field] = extra

        return super().get_uniqueness_extra_kwargs(field_names, declared_fields, extra_kwargs)

    def to_internal_value(self: Union["Serializer", "ProjectMixin"], data):
        """
        Overridden DRF function where we set project field value, before record is saved to database.
        We do this only if project field is not shown on form.
        Project must be defined in request.selected_project attribute
        """
        from django_project_base.base.permissions import project_is_selected

        if project_fields := self.get_project_fields():
            request = self.context.get("request", None)
            project_field_shown = self.should_show_project_field()
            selected_project = getattr(request, "selected_project", None)
            if not project_field_shown and request and project_is_selected(selected_project):
                for field_name in project_fields:
                    data._mutable = True
                    data[field_name] = selected_project.pk
                    data._mutable = False

        return super().to_internal_value(data)
