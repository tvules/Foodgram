from django.db import models

from .validators import HEXColorValidator


class HEXColorField(models.CharField):
    default_validators = [HEXColorValidator]

    def __init__(self, *args, max_length=7, **kwargs):
        super().__init__(*args, max_length=max_length, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        if isinstance(value, str):
            return value.upper()
        return value
