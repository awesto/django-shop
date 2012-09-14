# -*- coding: utf-8 -*-
from decimal import Decimal
from django.db.models.fields import DecimalField


class CurrencyField(DecimalField):
    """
    A CurrencyField is simply a subclass of DecimalField with a fixed format:
    decimal_places=2, and defaults to 0.00

    You can specify max-digits here, otherwise it will default to 20
    """
    def __init__(self, **kwargs):
        # Remove decimal places from kwargs, we only want 2
        if 'decimal_places' in kwargs.keys():
            del kwargs['decimal_places']

        # get "default" or 0.00
        default = kwargs.get('default', Decimal('0.00'))
        # get "max_digits" or 20
        max_digits = kwargs.get('max_digits', 20)

        # Now remove the keys from kwargs, otherwise we will pass them at 
        # double in the super() call below
        if 'default' in kwargs.keys():
            del kwargs['default']
        if 'max_digits' in kwargs.keys():
            del kwargs['max_digits']

        super(CurrencyField, self).__init__(max_digits=max_digits,
            decimal_places=2, default=default, **kwargs)

    def south_field_triple(self):  # pragma: no cover
        """
        Returns a suitable description of this field for South.
        This is excluded from coverage reports since it is pretty much a piece
        of South itself, and does not influence program behavior at all in
        case we don't use South.
        """
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.DecimalField"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)
