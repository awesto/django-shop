from django.utils.six import PY2

if PY2:
    from .choice_enum2 import ChoiceEnum
else:
    from .choice_enum3 import ChoiceEnum


__all__ = ['ChoiceEnum']
