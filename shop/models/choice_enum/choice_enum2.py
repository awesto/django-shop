# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from enum import Enum

from django.utils.translation import ugettext

from .choice_enum_meta import ChoiceEnumMeta


class ChoiceEnum(Enum):
    """
    Utility class to handle choices in Django model fields
    """
    __metaclass__ = ChoiceEnumMeta

    def __str__(self):
        return ugettext('.'.join((self.__class__.__name__, self.name)))

    __unicode__ = __str__

    @classmethod
    def default(cls):
        try:
            return next(iter(cls))
        except StopIteration:
            return None

    @classmethod
    def choices(cls):
        choices = [(c.value, str(c)) for c in cls]
        return choices
