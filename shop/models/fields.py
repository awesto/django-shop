# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import enum

from django.conf import settings
from django.db import models
from django.utils.six import python_2_unicode_compatible, with_metaclass, string_types
from django.utils.translation import ugettext_lazy


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


class ChoiceEnumMeta(enum.EnumMeta):
    def __call__(cls, value, *args, **kwargs):
        if isinstance(value, string_types):
            try:
                value = cls.__members__[value]
            except KeyError:
                pass  # let the super method complain
        return super(ChoiceEnumMeta, cls).__call__(value, *args, **kwargs)


@python_2_unicode_compatible
class ChoiceEnum(with_metaclass(ChoiceEnumMeta, enum.Enum)):
    """
    Utility class to handle choices in Django model fields
    """
    def __str__(self):
        return self.name

    @classmethod
    def default(cls):
        try:
            return next(iter(cls.__members__.values()))
        except StopIteration:
            return None

    @classmethod
    def choices(cls):
        values = [p.value for p in cls.__members__.values()]
        if len(values) > len(set(values)):
            msg = "Duplicate values found in {}".format(cls.__class__.__name__)
            raise ValueError(msg)
        choices = [(prop.value, ugettext_lazy('.'.join((cls.__name__, attr))))
                   for attr, prop in cls.__members__.items()]
        return choices


class ChoiceEnumField(models.PositiveSmallIntegerField):
    description = ugettext_lazy("Customer recognition state")

    def __init__(self, *args, **kwargs):
        self.enum_type = kwargs.pop('enum_type', ChoiceEnum)
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
        return self.enum_type(value)

    def get_prep_value(self, state):
        return state.value

    def to_python(self, state):
        return self.enum_type(state)
