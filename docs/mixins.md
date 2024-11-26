# ProjectMixin Documentation

## Overview

The `ProjectMixin` class is a Django mixin intended for use with serializers that include a project field. This mixin 
handles the visibility and validation of the project field based on the 
[DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE](./project.md#django_project_base_selected_project_mode) setting. 
The mixin ensures that users can only select from their permitted projects when the selection mode is set to 
`SelectedProjectMode.PROMPT`.

## Attributes

### `PROJECT_FIELD`
- **Type**: `str`
- **Default**: `"project"`
- **Description**: Defines the name of the project field in the serializer. If your serializer uses a different field 
name for the project, you should override this attribute. If your serializer have multiple project fields define them in 
list of strings

## Methods

### `should_show_project_field()`
- **Parameters**: `self: Union["Serializer", "ProjectMixin"]`
- **Returns**: `bool`
- **Description**: Determines whether the project field should be shown in the serializer. The field is shown only if 
the `DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE` is set to `SelectedProjectMode.PROMPT` and the user has permission to 
select from more than one project.

### `get_project_fields()`
- **Parameters**: `self: Union["Serializer", "ProjectMixin"]`
- **Returns**: `List[str]`
- **Description**: Retrieves the list of fields in the serializer that refer to the project. By default, it returns a 
list containing the `PROJECT_FIELD` attribute. If multiple fields refer to the project, override this attribute in the 
serializer. The `PROJECT_FIELD` can be either a string or a list of strings.

### `get_available_projects()`
- **Parameters**: `self: Union["Serializer", "ProjectMixin"]`
- **Returns**: `QuerySet`
- **Description**: Returns a queryset of projects that the user is allowed to choose from in the form. The queryset is 
filtered based on the user's permissions.

### `build_relational_field()`
- **Parameters**: 
  - `self: Union["Serializer", "ProjectMixin"]`
  - `field_name: str`
  - `relation_info`
- **Returns**: `(field_class, field_kwargs)`
- **Description**: Overrides the default DRF (Django Rest Framework) method for building relational fields. If the field
corresponds to a project field and is not explicitly declared in the serializer, this method uses the 
[ProjectField](./fields.md#projectfield) class.

### `get_uniqueness_extra_kwargs()`
- **Parameters**: 
  - `self: Union["Serializer", "ProjectMixin"]`
  - `field_names: List[str]`
  - `declared_fields: Dict`
  - `extra_kwargs: Dict`
- **Returns**: `Dict`
- **Description**: Overrides the default DRF method to set or prepare the `display` and `queryset` attributes for 
project fields. If the project field should be shown, it sets the display mode to `FULL` and populates the queryset with
the available projects. Otherwise, it hides the project field.

### `to_internal_value()`
- **Parameters**: 
  - `self: Union["Serializer", "ProjectMixin"]`
  - `data: dict`
- **Returns**: `dict`
- **Description**: Overrides the default DRF method to set the project field's value before saving the record to the 
database. This is done only if the project field is not shown in the form. The project is taken from the 
`request.selected_project` attribute.

## Usage

To use `ProjectMixin`, include it in your serializer classes that involve project selection. Ensure that the necessary
settings (`DJANGO_PROJECT_BASE_SELECTED_PROJECT_MODE`) are configured correctly to control how and when the project 
field is displayed.

```python
from rest_framework import serializers
from your_app.models import YourModel
from your_app.mixins import ProjectMixin

class YourSerializer(ProjectMixin, serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = '__all__'
