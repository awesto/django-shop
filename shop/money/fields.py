# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from django.core.exceptions import ValidationError
from django import forms
from django.db import models
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from shop import settings as shop_settings
from .money_maker import MoneyMaker, AbstractMoney
from .iso4217 import CURRENCIES


class MoneyFieldWidget(forms.widgets.NumberInput):
    """
    Replacement for NumberInput widget adding the currency suffix.
    """
    def __init__(self, attrs=None):
        defaults = {'style': 'width: 75px; text-align: right'}
        try:
            self.currency_code = attrs.pop('currency_code')
            defaults.update(attrs)
        except (KeyError, TypeError):
            raise ValueError("MoneyFieldWidget must be instantiated with a currency_code.")
        super(MoneyFieldWidget, self).__init__(defaults)

    def render(self, name, value, attrs=None):
        input_field = super(MoneyFieldWidget, self).render(name, value, attrs)
        return format_html('{} <strong>{}</strong>', input_field, self.currency_code)


class MoneyFormField(forms.DecimalField):
    """
    Use this field type in Django Forms instead of a DecimalField, whenever a input field for
    the Money representation is required.
    """
    def __init__(self, money_class=None, **kwargs):
        self.Money = money_class
        super(MoneyFormField, self).__init__(**kwargs)

    def prepare_value(self, value):
        if isinstance(value, AbstractMoney):
            return Decimal(value)
        return value

    def to_python(self, value):
        value = super(MoneyFormField, self).to_python(value)
        return self.Money(value)

    def validate(self, value):
        if value.currency != self.Money.currency:
            raise ValidationError("Can not convert different Money types.")
        super(MoneyFormField, self).validate(Decimal(value))
        return value


class MoneyField(models.DecimalField):
    """
    A MoneyField shall be used to store money related amounts in the database, keeping track of
    the used currency. Accessing a model field of type MoneyField, returns a MoneyIn<CURRENCY> type.
    """
    description = _("Money in %(currency_code)s")

    def __init__(self, *args, **kwargs):
        self.currency_code = kwargs.pop('currency', shop_settings.DEFAULT_CURRENCY)
        self.Money = MoneyMaker(self.currency_code)
        defaults = {
            'max_digits': 30,
            'decimal_places': CURRENCIES[self.currency_code][1],
            'default': self.Money(0) if kwargs.get('null', False) else self.Money(),
        }
        defaults.update(kwargs)
        super(MoneyField, self).__init__(*args, **defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(MoneyField, self).deconstruct()
        if kwargs['max_digits'] == 30:
            kwargs.pop('max_digits')
        if kwargs['decimal_places'] == CURRENCIES[self.currency_code][1]:
            kwargs.pop('decimal_places')
        kwargs.pop('default')
        return name, path, args, kwargs

    def to_python(self, value):
        if isinstance(value, AbstractMoney):
            return value
        if value is None:
            return self.Money('NaN')
        value = super(MoneyField, self).to_python(value)
        return self.Money(value)

    def get_prep_value(self, value):
        # force to type Decimal by using grandparent super
        value = super(models.DecimalField, self).get_prep_value(value)
        return super(MoneyField, self).to_python(value)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return
        if isinstance(value, float):
            value = str(value)
        return self.Money(value)

    def get_db_prep_save(self, value, connection):
        if value.is_nan():
            return None
        return super(MoneyField, self).get_db_prep_save(value, connection)

    def get_prep_lookup(self, lookup_type, value):
        if isinstance(value, AbstractMoney):
            if value.get_currency() != self.Money.get_currency():
                msg = "This field stores money in {}, but the lookup amount is in {}"
                raise ValueError(msg.format(value.get_currency(), self.Money.get_currency()))
            value = value.as_decimal()
        result = super(MoneyField, self).get_prep_lookup(lookup_type, value)
        return result

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        # grandparent super
        value = super(models.DecimalField, self).get_prep_value(value)
        return self.to_python(value)

    def formfield(self, **kwargs):
        widget = MoneyFieldWidget(attrs={'currency_code': self.Money.currency})
        defaults = {'form_class': MoneyFormField, 'widget': widget, 'money_class': self.Money}
        defaults.update(**kwargs)
        formfield = super(MoneyField, self).formfield(**defaults)
        return formfield
