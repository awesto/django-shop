# -*- coding: utf-8 -*-
from enum import EnumMeta

from django.utils.six import string_types


class ChoiceEnumMeta(EnumMeta):
    def __call__(cls, value, *args, **kwargs):
        if isinstance(value, string_types):
            try:
                value = cls.__members__[value]
            except KeyError:
                pass  # let the super method complain
        return super(ChoiceEnumMeta, cls).__call__(value, *args, **kwargs)
