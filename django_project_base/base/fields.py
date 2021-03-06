from django.core.validators import RegexValidator
from django.db.models import fields


class HexColorField(fields.CharField):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 7
        super().__init__(*args, **kwargs)
        self.validators.append(RegexValidator(
            regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
            message='Value is not a hex color',
        ))
