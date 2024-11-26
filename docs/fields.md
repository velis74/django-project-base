# Fields

## HEXColorField

Field with validator for color in hex format, currently used for setting background color for Tags.

## ProjectField

Use this class for project related fields. Field will be hidden on form or table if not needed. If needed it will 
include only projects that user has rights to. This is done by [ProjectMixin](mixins.md#project-mixin) that should be 
mixed in serializers that have project related fields.




