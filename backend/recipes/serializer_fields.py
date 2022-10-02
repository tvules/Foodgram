from collections import OrderedDict

from rest_framework import serializers


class CustomPKRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        self.serializer_repr_class = kwargs.pop('serializer_repr_class', None)
        if self.serializer_repr_class is not None:
            assert issubclass(
                self.serializer_repr_class, serializers.BaseSerializer
            ), (
                'The `serializer_repr_class` argument must inherit '
                'from `rest_framework.serializers.BaseSerializer`.'
            )
        super().__init__(**kwargs)

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict(
            [
                (
                    super().to_representation(item),
                    self.display_value(item),
                )
                for item in queryset
            ]
        )

    def to_representation(self, value):
        if self.serializer_repr_class is not None:
            return self.serializer_repr_class(value).data
        return super().to_representation(value)
