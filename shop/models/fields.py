# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .choice_enum import ChoiceEnum

postgresql_engine_names = [
    'django.db.backends.postgresql',
    'django.db.backends.postgresql_psycopg2',
]

if settings.DATABASES['default']['ENGINE'] in postgresql_engine_names:
    from django.contrib.postgres.fields import JSONField as _JSONField
else:
    from jsonfield.fields import JSONField as _JSONField


class JSONField(_JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'default': {}})
        super(JSONField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(JSONField, self).deconstruct()
        del kwargs['default']
        return name, path, args, kwargs


class ChoiceEnumField(models.PositiveSmallIntegerField):
    description = _("Customer recognition state")

    def __init__(self, *args, **kwargs):
        self.enum_type = kwargs.pop('enum_type', ChoiceEnum)  # fallback is required form migrations
        if not issubclass(self.enum_type, ChoiceEnum):
            raise ValueError("enum_type must be a subclass of `ChoiceEnum`.")
        kwargs.update(choices=self.enum_type.choices())
        kwargs.setdefault('default', self.enum_type.default())
        super(ChoiceEnumField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(ChoiceEnumField, self).deconstruct()
        if 'choices' in kwargs:
            del kwargs['choices']
        if kwargs['default'] is self.enum_type.default():
            del kwargs['default']
        elif isinstance(kwargs['default'], self.enum_type):
            kwargs['default'] = kwargs['default'].value
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection, context):
        try:
            return self.enum_type(value)
        except ValueError:
            return value

    def get_prep_value(self, state):
        if isinstance(state, self.enum_type):
            return state.value
        if isinstance(state, int):
            return state
        raise ValueError("Value must be of type {}".format(self.enum_type))

    def to_python(self, state):
        return self.enum_type(state)

    def value_to_string(self, obj):
        if not isinstance(obj, self.enum_type):
            raise ValueError("Value must be of type {}".format(self.enum_type))
        return obj.name
