from enum import Enum

from django.utils.translation import ugettext

from .choice_enum_meta import ChoiceEnumMeta


class ChoiceEnum(Enum, metaclass=ChoiceEnumMeta):
    """
    Utility class to handle choices in Django model fields
    """
    def __str__(self):
        return ugettext('.'.join((self.__class__.__name__, self.name)))

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
