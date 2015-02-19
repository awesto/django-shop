# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db.models.fields import DecimalField
from django.db.models import SubfieldBase
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils import six
from shop import settings as shop_settings
from .iso4217 import CURRENCIES
from .money_maker import MoneyMaker


@python_2_unicode_compatible
class MoneyField(six.with_metaclass(SubfieldBase, DecimalField)):
    """
    A MoneyField shall be used to store money related amounts in the database, keepinf track of
    the used currency. Accessing a model field of type MoneyField, returns a MoneyIn... type.
    """
    def __init__(self, **kwargs):
        currency_code = kwargs.pop('currency', shop_settings.DEFAULT_CURRENCY)
        self.Money = MoneyMaker(currency_code)
        defaults = {
            'max_digits': 30,
            'decimal_places': CURRENCIES[currency_code][1],
        }
        defaults.update(kwargs, default=self.Money())
        super(MoneyField, self).__init__(**defaults)

    def __str__(self):
        return force_text(self)

    def to_python(self, value):
        if value is None:
            return value
        try:
            return self.Money(value)
        except InvalidOperation:
            raise ValidationError(
                self.error_messages['invalid'], code='invalid', params={'value': value},
            )

    def deconstruct(self):
        """
        Required for Django migrations.
        """
        name, _, args, kwargs = super(MoneyField, self).deconstruct()
        path = 'django.db.models.fields.DecimalField'
        return name, path, args, kwargs

    def south_field_triple(self):  # pragma: no cover
        """
        Returns a suitable description of this field for South.
        This is excluded from coverage reports since it is pretty much a piece
        of South itself, and does not influence program behavior at all in
        case we don't use South.
        """
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.DecimalField'
        args, kwargs = introspector(self)
        return field_class, args, kwargs
